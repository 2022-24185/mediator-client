class WorkerManager:
    def __init__(self):
        self.workers = []

    def start_worker(self, worker):
        self.workers.append(worker)
        worker.finished.connect(lambda: self.workers.remove(worker))
        worker.start()

    def stop_all_workers(self):
        for worker in self.workers:
            worker.quit()
            worker.wait()
            self.workers.remove(worker)
    
    def wait_for_all_workers(self):
        for worker in self.workers:
            worker.wait()
            self.workers.remove(worker)

    def get_number_of_workers(self):
        return len(self.workers)
    
    def get_workers(self):
        return self.workers
    