from flask import Flask, render_template, request, redirect
from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import CDN
from bokeh.charts import Bar, Line
from bokeh.io import gridplot,vplot
from bokeh.models import HoverTool
import pandas as pd
import numpy as np
import pickle
import itertools
import nltk


app = Flask(__name__)

@app.route('/')
def main():
  return redirect("/welcome")

@app.route('/welcome')
def welcome():
  page_title='Choose Healthy'
  pagetext='You can\'t control everything about your health. Take advantage of something you can control: the food you eat.'
  return render_template('welcome.html', page_title=page_title,pagetext=pagetext)

@app.route('/background')
def background():
  page_title = "Background"
  script0 = pickle.load(open('script_0.p','rb'))
  div0 = pickle.load(open('div_0.p','rb'))
  
  script1a = pickle.load(open('script_1a.p','rb'))
  div1a = pickle.load(open('div_1a.p','rb'))

  script1b = pickle.load(open('script_1b.p','rb'))
  div1b = pickle.load(open('div_1b.p','rb'))

  script2a = pickle.load(open('script_2a.p','rb'))
  div2a = pickle.load(open('div_2a.p','rb'))
  script2b = pickle.load(open('script_2b.p','rb'))
  div2b = pickle.load(open('div_2b.p','rb'))

  script3 = pickle.load(open('script_3.p','rb'))
  div3 = pickle.load(open('div_3.p','rb'))
    
  return render_template('backgroundpage.html',page_title=page_title,script0=script0,div0=div0,script1a=script1a,script2a=script2a,div1a=div1a,div2a=div2a,script3=script3,div3=div3,script1b=script1b,div1b=div1b,script2b=script2b, div2b=div2b)


@app.route('/grocerylist', methods=['GET','POST'])
def grocerylist():
  page_title = "Let's start a grocery list"
  pagetext = 'Enter an ingredient and we\'ll show you other ingredients you\'ll need to make popular recipes'
  pagetext2 = 'These are good to have on hand:'
  top_ingreds = pickle.load(open('top_ingreds.p','rb'))
  top_ingreds = [x[0] for x in top_ingreds]
  if request.method=='GET':
      return render_template('grocerylist.html', page_title=page_title, pagetext=pagetext,top_ingreds=top_ingreds,pagetext2=pagetext2)
  else:
      ingred_of_int = request.form['ingred_of_int']
      return redirect('/newlist/'+ingred_of_int)

@app.route('/newlist/<ingred_of_int>', methods=['GET','POST'])
def newlist(ingred_of_int):
  page_title = "Here's your new grocery list"
  pagetext = 'Here are some ingredients that go well with ' + ingred_of_int + ':'
  ingred_pairs = pickle.load(open('ingred_pairs.p','rb'))
  top_ingreds = pickle.load(open('top_ingreds.p','rb'))
  prices = pickle.load(open('prices.p','rb'))
  pick_pairs = list(itertools.ifilter(lambda x: ingred_of_int in x, ingred_pairs))
  grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != ingred_of_int else pick_pairs[x][1] for x in range(len(pick_pairs))]

  top_ingreds = [x[0] for x in top_ingreds]
  grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]

  if len(grocery_list) == 0:
        if ingred_of_int[-1] == 'y':
            try_ingred = ingred_of_int[:-1] + 'ies'
            pick_pairs = list(itertools.ifilter(lambda x: try_ingred in x, ingred_pairs))
            grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != try_ingred else pick_pairs[x][1] for x in range(len(pick_pairs))]
            grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]
        elif ingred_of_int[-3:] == 'ies':
            try_ingred = ingred_of_int[:-3] + 'y'
            pick_pairs = list(itertools.ifilter(lambda x: try_ingred in x, ingred_pairs))
            grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != try_ingred else pick_pairs[x][1] for x in range(len(pick_pairs))]
            grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]
            
  if grocery_list == []:
      try_ingred = ingred_of_int + 'es'
      pick_pairs = list(itertools.ifilter(lambda x: try_ingred in x, ingred_pairs))
      grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != try_ingred else pick_pairs[x][1] for x in range(len(pick_pairs))]
      grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]
  if grocery_list == []:
      try_ingred = ingred_of_int + 's'
      pick_pairs = list(itertools.ifilter(lambda x: try_ingred in x, ingred_pairs))
      grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != try_ingred else pick_pairs[x][1] for x in range(len(pick_pairs))]
      grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]
  if grocery_list == []:
      try_ingred = ingred_of_int[:-1]
      pick_pairs = list(itertools.ifilter(lambda x: try_ingred in x, ingred_pairs))
      grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != try_ingred else pick_pairs[x][1] for x in range(len(pick_pairs))]
      grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]
  if grocery_list == []:
      try_ingred = ingred_of_int[:-2]
      pick_pairs = list(itertools.ifilter(lambda x: try_ingred in x, ingred_pairs))
      grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != try_ingred else pick_pairs[x][1] for x in range(len(pick_pairs))]
      grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]

  price_list = []
  total_cost = 0
  for item in grocery_list:
      if prices[item][0] == 'sorry no price':
          price_list.append(item + '...................' + 'not listed')
      elif len(prices[item]) == 1:
          price_list.append(item + '...................' + prices[item][0])
          total_cost += float(prices[item][0].split()[1])
      elif len(prices[item]) == 2:
          price_list.append(item + '....................' + prices[item][0] + '*')
          total_cost += float(prices[item][0].split()[1])
  price_list1 = price_list[:15]
  price_list2 = price_list[15:]
  if len(price_list1) == 0:
    price_list1 = ['Sorry, no recipes were found using this ingredient']
  return render_template('newlist.html', page_title=page_title, pagetext=pagetext, price_list1=price_list1,price_list2=price_list2)

@app.route('/recipefinder', methods=['GET','POST'])
def recipefinder():
  page_title = "Recipe Finder"
  pagetext = 'Enter 1-3 ingredients to get recipe suggestions'
  if request.method=='GET':
      return render_template('recipefinder.html', page_title=page_title, pagetext=pagetext)
  else:
      ingred_of_int1 = request.form['ingred_of_int1']
      ingred_of_int2 = request.form['ingred_of_int2']
      ingred_of_int3 = request.form['ingred_of_int3']
      ingredients = '-'.join([ingred_of_int1,ingred_of_int2,ingred_of_int3])
      return redirect('/recipes/'+ingredients)
   
@app.route('/recipes/<ingredients>', methods=['GET','POST'])
def recipes(ingredients):
    nltk.data.path.append('./nltk_data/')
    n_display = 7
    use_ingreds = ingredients.split('-')
    use_ingreds = [x for x in use_ingreds if x != '']
    n_ingreds = len(use_ingreds)
    ingred_by_recipe = pickle.load(open('ingred_by_recipes.p','rb'))
    suggest_recipes = []
    uselemmatizer = pickle.load(open('uselemmatizer.p','rb'))
    lemmatized_ingreds = [uselemmatizer.lemmatize(x) for x in use_ingreds]
    for recipe in ingred_by_recipe:
        newlist = ingred_by_recipe[recipe][3]
        curr_ingreds = [uselemmatizer.lemmatize(x) for x in newlist if x != None]
        count = 0
        n_recipes = 0
        for n in xrange(n_ingreds):
            if lemmatized_ingreds[n] in curr_ingreds:
                count += 1
        if count == n_ingreds:
            add_recipe = (ingred_by_recipe[recipe][:-1])
            suggest_recipes.append(add_recipe)
            n_recipes += 1
    if len(suggest_recipes) < n_display:
        use_recipes = suggest_recipes
    else:
        randnums = np.random.choice(len(suggest_recipes), n_display)
        use_recipes = [suggest_recipes[x] for x in randnums]
    use_recipes = lemmatized_ingreds
    if n_ingreds == 0:
        print_ingred = 'Please enter an ingredient'
    elif n_ingreds == 1:
        print_ingred = 'Here are some recipes using ' + use_ingreds[0] + ':'
    elif n_ingreds == 2:
        print_ingred = 'Here are some recipes using ' + use_ingreds[0] + ' and ' + use_ingreds[1] + ':'
    elif n_ingreds == 3:
        print_ingred = 'Here are some recipes using ' + use_ingreds[0] + ', ' + use_ingreds[1] + ', and ' + use_ingreds[2] + ':'
    return render_template('recipes.html', print_ingred = print_ingred, use_recipes = use_recipes)

if __name__ == '__main__':
  app.run(port=33507)
