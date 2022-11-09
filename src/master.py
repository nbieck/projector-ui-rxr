import random
import queue
from multiprocessing.managers import BaseManager


# queue for sending tasks
task_queue = queue.Queue()
# queue for receiving result
result_queue = queue.Queue()


class QueueManager(BaseManager):
    pass


# 2つのキューをAPIとして登録する
# Windowsの場合はAPI登録にlambdaが使えないので、素直に関数を定義してください
QueueManager.register('get_task_queue', callable=lambda: task_queue)
QueueManager.register('get_result_queue', callable=lambda: result_queue)

# ポート5000を使い、認証暗号を'abc'にする
# Windowsの場合はアドレスを明記する必要がある（127.0.0.1）
manager = QueueManager(address=('', 5000), authkey=b'abc')
# 起動する
manager.start()
# ネット経由でキューオブジェクトを取得
task = manager.get_task_queue()
result = manager.get_result_queue()

# タスクを入れてみる
for i in range(10):
    n = random.randint(0, 10000)
    print('Put task {}...'.format(n))
    task.put(n)

# resultキューから結果を受け取る
print('Try get results...')
for i in range(10):
    # 10秒超えたらtimeoutで終了
    r = result.get(timeout=10)
    print('Result: {}'.format(r))

# 終了
manager.shutdown()
print('master exit.')