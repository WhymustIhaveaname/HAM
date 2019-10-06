#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#take s'=0.1875 we get:
#0.7857 0.1071               0.2142 0.1071
#0.0694(-2.67)               14.41
#0.8636 0.0681 0.5000 0.0681 0.5000 0.0681 0.1363 0.0681
#0.0005(-5.34) 1             1             208.7
import sqlite3,re,time,random,pygame
from math import tanh
class ham():
    thre=4.6
    batch_num=10
    len_no_repeat=5
    def __init__(self,user="defult"):
        self.user=user
        self.prevs=[""]*ham.len_no_repeat
        self.init_qs()
        self.check_table()
    def check_table(self):
        conn=sqlite3.connect("ham_data.db")
        cur=conn.cursor()
        cur.execute("select name from sqlite_master where type='table'")
        table_names=[i[0] for i in cur.fetchall()]
        if self.user not in table_names:
            cur.execute("create table %s(num text,avg single,std single,time int,hist text)"%(self.user))
            conn.commit()
            print("create table for user %s"%(self.user))
        conn.close()
    def init_qs(self):
        self.qs={}
        with open("./v171031/A.txt","rb") as f:
            s=f.read().decode("gbk")
        qs=re.findall("\[I\].+?\[P\]",s,re.S)
        for q in qs:
            lines=q.split("\r\n")
            self.qs[lines[0][3:]]=[lines[1][3:],lines[2][3:],lines[3][3:],lines[4][3:],lines[5][3:]]
        print("inited questions: %d"%(len(self.qs)))
    def get_randq(self):
        conn=sqlite3.connect("ham_data.db")
        cur=conn.cursor()
        cur.execute("select num,avg,std from %s"%(self.user))
        datas=cur.fetchall()
        conn.close()
        ax=0;pool=[];names=[]
        for i in datas:
            names.append(i[0])
            ratio=(2*i[1]-1)/(2*i[2])
            #print(i,ratio)
            if ratio<ham.thre:
                pool.append(i[0])
                ax+=1 
        if ax<ham.batch_num:
            ax=0
            for k in self.qs:
                if ax>=(ham.batch_num)/2 and len(pool)>0:
                    break
                if k not in names:
                    pool.append(k)
                    self.insert_db(k,0.5,0.25)
                    ax+=1
        if len(pool)==0:
        	return None,None,None
        #print(pool)
        for i in range(10):
            k=random.choice(pool)
            if k not in self.prevs:
            	break
        self.prevs[0:ham.len_no_repeat-1]=self.prevs[1:ham.len_no_repeat]
        self.prevs[ham.len_no_repeat-1]=k
        order=[1,2,3,4]
        random.shuffle(order)
        if order[0]==1:
            ans="A"
        elif order[1]==1:
        	ans="B"
        elif order[2]==1:
        	ans="C"
        elif order[3]==1:
        	ans="D"
        s="%s\n%s\n"%(k,self.qs[k][0])
        s+="[A]%s\n"%(self.qs[k][order[0]])
        s+="[B]%s\n"%(self.qs[k][order[1]])
        s+="[C]%s\n"%(self.qs[k][order[2]])
        s+="[D]%s\n"%(self.qs[k][order[3]])
        return k,s,ans
    def main(self):
        pygame.mixer.init()
        while True:
            k,s_print,ans=self.get_randq()
            if k==None:
            	print("congratulations! you have finished learning all the questions!")
            	return
            print(s_print,end="")
            while True:
                ans_prime=input()
                if len(ans_prime)==1 and ans_prime[0].upper() in ("A","B","C","D","S"):
            	    ans_prime=ans_prime.upper()
            	    break
                if len(ans_prime)==2 and ans_prime[0].upper()=="H":
                    ans_prime=ans_prime.upper()
                    break
                print("parse error")
            if ans_prime=="S":
            	continue
            elif ans_prime[0]=="H":
                if ans_prime[1]==ans:
                    pygame.mixer.music.load("./media/add_score.wav")
                    pygame.mixer.music.play()
                    print("this question will never show again")
                    self.insert_db(k,1,s=0.01)
                else:
                    pygame.mixer.music.load("./media/lose1.wav")
                    pygame.mixer.music.play()
                    print("but you give the wrong answer")
                    self.insert_db(k,0)
            elif ans_prime==ans:
                pygame.mixer.music.load("./media/add_score.wav")
                pygame.mixer.music.play()
                print("correct")
                self.insert_db(k,1)
            else:
                pygame.mixer.music.load("./media/lose1.wav")
                pygame.mixer.music.play()
                print("wrong! correct ans is: %s"%(ans))
                self.insert_db(k,0)
    def insert_db(self,k,a,s=0.1875):
        conn=sqlite3.connect("ham_data.db")
        cur=conn.cursor()
        cur.execute("select * from %s where num=?"%(self.user),(k,))
        temp=cur.fetchall()
        t=int(time.time())
        if len(temp)==0:
        	cur.execute("insert into %s (num,avg,std,time,hist) values(?,?,?,?,?)"%(self.user),
        		        (k,a,s,t,"(%d)%.1f,"%(t,a)))
        else:
        	a0=temp[0][1];s0=temp[0][2]+0.02+0.25*tanh(max(t-int(temp[0][3]),0)/(5*24*60*60))
        	a2,s2=ham.kalman(a0,s0,a,s)
        	cur.execute("update %s set avg=?,std=?,time=?,hist=? where num=?"%(self.user),(a2,s2,t,temp[0][4]+"(%d)%d,"%(t,a),k))
        conn.commit()
        conn.close()
    def kalman(a0,s0,a1,s1):
        de=s0+s1
        a=(a0*s1+a1*s0)/de
        s=(s0*s1)/de
        return a,s

if __name__=="__main__":
    #print(ham.kalman(1,0.1875,1,0.1875))
    name=input("your name(enter to use default):")
    if name=="":
        h=ham()
    else:
    	h=ham(name)
    h.main()
