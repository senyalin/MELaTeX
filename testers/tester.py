from calendar import c
import os
import difflib
import Levenshtein
from nltk.translate.bleu_score import sentence_bleu
from pylatexenc.latexwalker import LatexWalker
w = LatexWalker(r"\dot{\rho_{i}}=V_{G}\tan\alpha_{i},\;i=1,2,3")
(nodelist, pos, len_) = w.get_latex_nodes(pos=0)

for i in range(len(nodelist)):
    print(nodelist[i].latex_verbatim())

def main():
    total_count = 0
    ac_count = 0
    total_ratio = 0
    missed = 0
    count = 0
    for i,file_name in enumerate(os.listdir("test_files")):
        # if i >300:
        #     break
        # print(file_name)
        with open("test_files/"+file_name+"/"+file_name+"result.txt", "r") as result:
            with open("test_files/"+file_name+"/"+file_name+".txt", "r") as answer:
                ans = answer.read()
                
                ans = ans.replace("%\n","",-1)
                ans = ans.replace("\\\\\n","\\\\",-1)
                
                
                ans = ans.split("\n")

                res = result.read().split("\n")
                
                for ans_line in ans[:-1]:
                    flag = False
                    for word in ["array","align","split","cases","matrix"]:
                        if word in ans_line:
                            flag = True
                    # if "frac" not in ans_line:
                    #     flag = True
                    if flag:
                        continue
                    total_count += 1
                    
                    res_lines = difflib.get_close_matches(ans_line,res,cutoff=0)
                    if not res_lines:
                        print("MISS:",ans_line)
                        missed+=1
                        continue
                    
                    
                    if res_lines[0] == ans_line:
                        ac_count += 1
                        print("AC!")
                    
                    print("ans: "+ans_line+"\n")
                    print("res: "+res_lines[0])
                    anss = [ans_line]
                    
                    ratio = sentence_bleu(ans,res_lines[0],weights=(0.25, 0.25, 0.25, 0.25))
                    print("ratio:",ratio)
                    total_ratio += ratio
                    count += 1
                    print("\n")
    print(total_count,ac_count)
    print(ac_count/total_count)
    print(missed)
    print("avg:",total_ratio/count)

if __name__ == "__main__":
    main()
