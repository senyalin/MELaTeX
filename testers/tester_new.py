from calendar import c
import os
import difflib
import Levenshtein
from nltk.translate.bleu_score import sentence_bleu
from pylatexenc.latexwalker import LatexWalker
from tools.mapping import *
def main():
    total_count = 0
    ac_count = 0
    total_ratio = 0
    missed = 0
    count = 0
    small_count = 0
    for i,test_case in enumerate(os.listdir("data2")):
        # if i >300:
        #     break
        # print(file_name)
        with open("data2/{}/{}.txt".format(test_case,test_case)) as answer:
            with open("data2/{}/{}result.txt".format(test_case,test_case)) as result:
                with open("img/{}/{}_latex.txt".format(test_case,test_case)) as img_result:
                    img = img_result.read().split("\n")
                    ans = answer.read().split("\n")[:-1]
                    res = result.read().split("\n")
                    for j,ans_line in enumerate(ans):
                        flag = False
                        flag2 = False
                        for word in ["lim"]:
                            if word in ans_line:
                                flag = True
                        # for word in big_operator.values():
                        #     if word in ans_line:
                        #         flag = True

                        # for word in ["sum"]:
                        #     if word in ans_line:
                        #         flag2 = True
                        
                        if flag:
                            continue
                        # if not flag2:
                        #     continue
                        total_count += 1
                        
                        
                        anss = [ans_line]
                        if len(ans_line)<4:
                            small_count+=1
                        ratio = sentence_bleu(res,ans_line,weights=(0.25, 0.25, 0.25, 0.25))
                        if ratio < 0.7 and img[4*j+2] != "Miss" and float(img[4*j+2]) < 0.7:
                            print(test_case,j)
                            print("ans: "+ans_line+"\n")
                            print("res: "+res[j])
                            print("ratio:",ratio)
                            print("img score:",img[4*j+2])
                            print("\n")
                        # if img[4*j+2] != "Miss" and float(img[4*j+2]) < 0.6:
                        #     print(test_case,j)
                        #     print("ans: "+ans_line+"\n")
                        #     print("res: "+res[j])
                        #     print("ratio:",ratio)
                        #     print("img score:",img[4*j+2])
                        #     print("\n")
                        total_ratio += ratio
                        count += 1
                        
                        # if res[j] == ans_line:
                        #     ac_count += 1
                        #     print("AC!")
    print(total_count,ac_count)
    print(ac_count/total_count)
    print("avg:",total_ratio/count)
               

if __name__ == "__main__":
    main()
