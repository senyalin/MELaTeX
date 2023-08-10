import LaTeX2img

total_score = 0
wrong = []
num = 0

for index in range(91795):
    try:
        a = LaTeX2img.lateximage(index)
        total_score += a
        num += 1
    except:
        wrong.append(index)
        with open ("wrong.txt", "a") as wr:
            for j in wrong:
                wr.write(str(j)+"\n")
        wrong = []

print("score:",total_score / num)