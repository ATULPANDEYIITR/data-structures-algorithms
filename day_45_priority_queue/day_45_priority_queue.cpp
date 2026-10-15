#include <algorithm>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Repository build-farm scheduling case study.
 *
 * A build farm receives compilation, test, security-scan, and deployment
 * jobs. It must prioritize urgent work, preserve FIFO order for ties,
 * reject duplicate identifiers, support queued-job cancellation and
 * reprioritization, and account for worker capacity.
 *
 * Compile: g++ -std=c++17 -Wall -Wextra -pedantic priority_queue.cpp -o priority_queue
 */

enum class JobState {
    Queued,
    Running,
    Completed,
    Cancelled,
    Failed
};

struct BuildJob {
    std::string id;
    std::string repository;
    std::string operation;
    int priority;
    int estimated_seconds;
    std::uint64_t sequence;
    JobState state = JobState::Queued;
};

struct JobOrder {
    bool operator()(const BuildJob& left, const BuildJob& right) const {
        // std::priority_queue places the element considered greatest first.
        // Reverse the priority comparison to put the highest score on top.
        if (left.priority != right.priority) {
            return left.priority < right.priority;
        }
        return left.sequence > right.sequence;
    }
};

class BuildFarm {
public:
    explicit BuildFarm(std::size_t worker_count)
        : worker_count_(worker_count) {
        if (worker_count_ == 0) {
            throw std::invalid_argument("At least one worker is required");
        }
    }

    void submit(std::string id,
                std::string repository,
                std::string operation,
                int priority,
                int estimated_seconds) {
        validate(id, repository, operation, priority, estimated_seconds);

        if (jobs_.find(id) != jobs_.end()) {
            throw std::invalid_argument("Duplicate job ID: " + id);
        }

        BuildJob job{
            std::move(id),
            std::move(repository),
            std::move(operation),
            priority,
            estimated_seconds,
            next_sequence_++,
            JobState::Queued
        };

        const std::string key = job.id;
        jobs_.emplace(key, job);
        queue_.push(job);
    }

    void reprioritize(const std::string& id, int priority) {
        if (priority < 0 || priority > 100) {
            throw std::invalid_argument("Priority must be between 0 and 100");
        }

        auto found = jobs_.find(id);
        if (found == jobs_.end() || found->second.state != JobState::Queued) {
            throw std::invalid_argument("Only queued jobs can be reprioritized");
        }

        // priority_queue has no efficient arbitrary-node update. Store the
        // authoritative job in the map, push a new queue entry, and discard
        // stale copies when dequeuing.
        found->second.priority = priority;
        found->second.sequence = next_sequence_++;
        queue_.push(found->second);
    }

    void cancel(const std::string& id) {
        auto found = jobs_.find(id);
        if (found == jobs_.end() || found->second.state != JobState::Queued) {
            throw std::invalid_argument("Only queued jobs can be cancelled");
        }
        found->second.state = JobState::Cancelled;
    }

    bool start_next() {
        if (running_ >= worker_count_) {
            return false;
        }

        while (!queue_.empty()) {
            BuildJob candidate = queue_.top();
            queue_.pop();

            auto found = jobs_.find(candidate.id);
            if (found == jobs_.end()) {
                continue;
            }

            BuildJob& current = found->second;

            // Compare both state and sequence to reject cancelled or stale
            // entries left behind by reprioritization.
            if (current.state != JobState::Queued ||
                current.sequence != candidate.sequence) {
                continue;
            }

            current.state = JobState::Running;
            ++running_;
            std::cout << "START " << current.id
                      << " repository=" << current.repository
                      << " operation=" << current.operation
                      << " priority=" << current.priority
                      << '\n';
            return true;
        }

        return false;
    }

    void finish(const std::string& id, bool success) {
        auto found = jobs_.find(id);
        if (found == jobs_.end() || found->second.state != JobState::Running) {
            throw std::invalid_argument("Job is not running: " + id);
        }

        found->second.state = success ? JobState::Completed : JobState::Failed;
        --running_;

        std::cout << (success ? "COMPLETE " : "FAIL ")
                  << id << '\n';
    }

    void print_report() const {
        std::cout << "\nBuild-farm report\n";

        for (const auto& pair : jobs_) {
            const BuildJob& job = pair.second;
            std::cout << job.id
                      << " priority=" << job.priority
                      << " estimated_seconds=" << job.estimated_seconds
                      << " state=" << state_name(job.state)
                      << '\n';
        }

        std::cout << "Running workers: " << running_
                  << "/" << worker_count_ << '\n';
    }

private:
    std::size_t worker_count_;
    std::size_t running_ = 0;
    std::uint64_t next_sequence_ = 0;
    std::priority_queue<BuildJob, std::vector<BuildJob>, JobOrder> queue_;
    std::unordered_map<std::string, BuildJob> jobs_;

    static void validate(const std::string& id,
                         const std::string& repository,
                         const std::string& operation,
                         int priority,
                         int estimated_seconds) {
        if (id.empty() || repository.empty() || operation.empty()) {
            throw std::invalid_argument("Job identity fields cannot be empty");
        }
        if (priority < 0 || priority > 100) {
            throw std::invalid_argument("Priority must be between 0 and 100");
        }
        if (estimated_seconds < 0) {
            throw std::invalid_argument("Duration cannot be negative");
        }
    }

    static const char* state_name(JobState state) {
        switch (state) {
            case JobState::Queued: return "queued";
            case JobState::Running: return "running";
            case JobState::Completed: return "completed";
            case JobState::Cancelled: return "cancelled";
            case JobState::Failed: return "failed";
        }
        return "unknown";
    }
};

int main() {
    try {
        std::cout << "=== Build-farm priority scheduling ===\n";
        BuildFarm farm(2);

        farm.submit("BUILD-201", "payments-api", "compile", 50, 40);
        farm.submit("TEST-202", "payments-api", "integration-tests", 70, 80);
        farm.submit("SEC-203", "identity-service", "security-scan", 95, 35);
        farm.submit("DEPLOY-204", "payments-api", "production-deploy", 85, 25);
        farm.submit("REPORT-205", "analytics-service", "report", 20, 15);

        farm.reprioritize("BUILD-201", 90);
        farm.cancel("REPORT-205");

        // Two workers may execute simultaneously. A third start is refused
        // until one running job finishes.
        farm.start_next();
        farm.start_next();

        if (!farm.start_next()) {
            std::cout << "Worker limit reached; dispatch paused.\n";
        }

        farm.finish("BUILD-201", true);
        farm.start_next();
        farm.finish("SEC-203", true);
        farm.start_next();
        farm.finish("DEPLOY-204", false);

        farm.print_report();

        std::cout << "\n=== Validation checks ===\n";
        try {
            farm.submit("INVALID", "repo", "compile", 101, 10);
        } catch (const std::invalid_argument& error) {
            std::cout << "Rejected invalid job: " << error.what() << '\n';
        }

        try {
            farm.finish("REPORT-205", true);
        } catch (const std::invalid_argument& error) {
            std::cout << "Rejected invalid transition: "
                      << error.what() << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Build-farm error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
