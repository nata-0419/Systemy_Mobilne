import math
import matplotlib.pyplot as plt
import time

current_state = int(time.time())

def set_seed(val):
    global current_state
    current_state = val

def gen_u():        #Generator liczb o rozkładzie równomiernym
    global current_state
    a = 16807
    b = 0
    c = 2147483647
    current_state = (a * current_state + b) % c
    return current_state / c

def gen_poisson(lam, n):    #generator liczb o rozkladzie poissona
    data = []
    q = math.exp(-lam)
    for _ in range(n):
        x = -1
        s = 1
        while s > q:
            u = gen_u()
            s *= u
            x += 1
        data.append(x)
    return data

def gen_normal(mu, sigma, n):   #Generator liczb o rozkładzie Normalnym
    data = []
    for _ in range((n // 2) + 1):
        u1 = gen_u()
        u2 = gen_u()
        x1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        x2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        data.append(mu + sigma * x1)
        data.append(mu + sigma * x2)
    return data[:n]

def main():
    use_seed = input("Czy użyć ziarna? (t/n): ")
    if use_seed.lower() == 't':
        val = int(input("Podaj ziarno: "))
        set_seed(val)

    n = int(input("Podaj ilość liczb: "))                           #liczba liczb
    lam = float(input("Podaj parametr lambda dla Poissona: "))      #rozklad Poissona
    mu = float(input("Podaj średnią mu dla rozkładu normalnego: ")) #rozklad normalny
    sigma = float(input("Podaj odchylenie sigma dla rozkładu normalnego: "))    #odchylenie

    poisson_results = gen_poisson(lam, n)
    normal_results = gen_normal(mu, sigma, n)

    plt.figure(figsize=(15, 5))
    plt.subplot(2, 1, 1)
    plt.hist(poisson_results, bins=range(max(poisson_results) + 2), align='left')
    plt.title("Rozkład Poissona")

    plt.subplot(1, 2, 1)
    plt.hist(normal_results, bins=30)
    plt.title("Rozkład Normalny")

    plt.show()

if __name__ == "__main__":
    main()