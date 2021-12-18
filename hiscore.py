import pickle
import os
import cfg
import random
from string import ascii_uppercase

ascii_uppercase += ' '


def reset():
    pass
    # hiscores_file = "hiscores.pickle"
    # if os.path.isfile(hiscores_file):
    #     os.remove(hiscores_file)


def load_in():
    try:
        infile = open("hiscores.pickle", "rb")
        cfg.hiscores = pickle.load(infile)
        infile.close()
    except OSError:
        # print('no file')
        random.choice(ascii_uppercase)
        for i in range(11):
            score = random.randrange(50, 3000, 50)
            who = random.choice(ascii_uppercase)
            who += random.choice(ascii_uppercase)
            who += random.choice(ascii_uppercase)
            # score = 0
            # who = '   '
            cfg.hiscores.append([score, who])

        outfile = open("hiscores.pickle", "wb")
        pickle.dump(sorted(cfg.hiscores, reverse=True)[:10], outfile)
        outfile.close()

        infile = open("hiscores.pickle", "rb")
        cfg.hiscores = pickle.load(infile)
        infile.close()

        # print('made new')
    finally:
        # print('done')
        # print(cfg.hiscores)
        pass


reset()
