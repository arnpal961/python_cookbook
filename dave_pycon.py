###############################
#        Die Threads          #
# thredo used by Dave Beazly  #
###############################

# dying philosopher problem
import threading
# import thredo
import random
import time

def philosopher(n):
    time.sleep(random.random())
    # thredo.sleep(random.random())
    with sticks[n]:
        time.sleep(random.random())
        # thredo.sleep(random.random())
        with sticks[(n+1) % 5]:
            print("eating", n)
            time.sleep(random.random())
            # thredo.sleep(random.random())

def main():
    # phils = [ thredo.spawn(philosopher, n) for n in range(5)]
    phils = [threading._start_new_thread(philosopher, n) for n in range(5)]
    for p in phils:
        p.wait()

if __name__=="__main__":
    # Die Threads 33:00
    # Deadlock condition
    sticks = [threading.Lock() for n in range(5)]
    threading._start_new_thread(main, ())
