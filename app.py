from flask import Flask, flash, render_template, request,redirect, session
import pymongo as py
app=Flask(__name__)
from flask_session import Session

from bson.objectid import ObjectId

app = Flask(__name__)

app.config["SECRET_KEY"]='65b0b774279de460f1cc5c92'
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'

Session(app)

# Configuration de la connexion MongoDB
myclient = py.MongoClient("mongodb+srv://firas:firas123@cluster0.7hm7zsb.mongodb.net/?retryWrites=true&w=majority")
# Création Base de données 
mydb = myclient["profil_users"]

#Création Collection
mycollection = mydb["users"]


# Création admin compte  
# mydoc={"nom":"firas","prenom":"hkimi","email":"f@gmail.com","password":"123","active":"1","role":"admin"}

# Check if admin account exist 
# admin = mycollection.find_one({"email":"f@gmail.com"})
# Create Account if not Exist
# if not(admin) :
#     mycollection.insert_one(mydoc)

# Sign Up 
@app.route('/signup',methods=["POST","GET"])
def signup():
    if  session.get('user_id'):
        return redirect('/dashboard')
    if  session.get('admin_id'):
        return redirect('/dashboard')
    if request.method=='POST':
        # get all input field name
        nom=request.form.get('nom')
        prenom=request.form.get('prenom')
        email=request.form.get('email')
        password=request.form.get('password')
        loisirs=request.form.get('loisirs')

        print(loisirs)


        # check all the field is filled are not
        if nom =="" or prenom=="" or email=="" or password=="" :
            flash('Veuillez remplir tous les champs','danger')
            return redirect('/signup')
        else:
            is_email = mycollection.find_one({"email": email})
            if is_email:
                flash('Email déjà existant','danger')
                return redirect('/signup')
            else:
                new_user = {
                    'nom': nom,
                    'prenom': prenom,
                    'email': email,
                    'password': password,
                    "loisirs":loisirs,
                    "active":0,
                    'role':"user"
                }

                # Insert the new user document into the collection
                user = mycollection.insert_one(new_user)
                flash('Administrateur approuvera votre compte dans 10 à 30 mint ','success')
                return redirect('/')
    else:
        return render_template('inscription.html',title="Inscription User")


# Sign In 
@app.route('/',methods=['POST','GET'])
def signin():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    # if  session.get('admin_id'):
    #     return redirect('/admin/dashboard')
    if request.method=="POST":
        # get the name of the field
        email=request.form.get('email')
        password=request.form.get('password')
        # check user exist in this email or not
        users = mycollection.find_one({"email": email})
        print(users)
        if users and users.get('password') == password :
            # check the admin approve your account are not
            is_active = mycollection.find_one({"email": users.get('email')})
            if is_active.get("active") == 0:
                flash('Votre compte n’est pas activée par l’administrateur','danger')
                return redirect('/')
            elif is_active.get("role") == "admin" :
                session['admin_id']=is_active.get('_id')
                session['admin_name']=is_active.get('nom')
                flash('Ouverture de session réussie','success')
                return redirect('/admin/dashboard')
            else:
                session['user_id']=is_active.get('_id')
                session['username']=is_active.get('nom')+" " +is_active.get('prenom')
                flash('Ouverture de session réussie','success')
                return redirect('/user/dashboard')
        else:
            flash('Email ou mot de passe non valides','danger')
            return redirect('/')
    else:
        return render_template('connexion.html',title="Login")

# Admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    # if not session.get('admin_id'):
    #     return redirect('/admin/')
    totalUser=mycollection.count_documents({"role":"user"}) # Liste des utilisateurs 
    totalActive=mycollection.count_documents({'active': 1}) # Liste des utilisateurs actives
    TotalNonActive=mycollection.count_documents({'active': 0}) # Liste des utilisateurs non actives
    return render_template('admin/dashboard.html',title="Admin Dashboard",totalUser=totalUser,totalApprove=totalActive,NotTotalApprove=TotalNonActive)


# admin get all user 
@app.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    # if not session.get('admin_id'):
    #     return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users = mycollection.find({"nom": {"$regex": search}})
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users = mycollection.find({"role":"user"})
        return render_template('admin/all-user.html',title='Approve User',users=users)


#Activation d'un utilisateur
@app.route('/admin/approve-user/<id>')
def adminApprove(id):
    # if not session.get('admin_id'):
    #     return redirect('/admin/')
    mycollection.update_one({'_id': ObjectId(id)},{'$set': {'active': 1}})
    flash('Activation avec succès','success')
    return redirect('/admin/get-all-user')

# change admin password
# @app.route('/admin/change-admin-password',methods=["POST","GET"])
# def adminChangePassword():
#     admin = mycollection.find_one({"role": "admin"})
#     if request.method == 'POST':
#         email=request.form.get('email')
#         password=request.form.get('password')
#         if email == "" or password=="":
#             flash('Veuillez remplir tous les champs','danger')
#             return redirect('/admin/change-admin-password')
#         else:
#             result = mycollection.update_one({"_id": ObjectId(admin["_id"])},{"$set": {"password": password}})
          
            
#             if result.acknowledged:
#                 flash('Mise à jour du mot de passe d’administrateur réussie','success')
#             else:
#                 print("Update operation not acknowledged")
#             return redirect('/admin/change-admin-password')
#     else:
#         return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)


# admin logout
# @app.route('/admin/logout')
# def adminLogout():
#     if not session.get('admin_id'):
#         return redirect('/admin/')
#     if session.get('admin_id'):
#         session['admin_id']=None
#         session['admin_name']=None
#         return redirect('/')


# user dashboard
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    user = mycollection.find_one({"_id": id})
    return render_template('user/dashboard.html',title="User Dashboard",user=user)


# user logout
@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/')

    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/')

# changer mot de passe d'un utilisateur
@app.route('/user/change-password',methods=["POST","GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        if email == "" or password == "":
            flash('Veuillez remplir tous les champs','danger')
            return redirect('/user/change-password')
        else:
            user = mycollection.find_one({"email": email})
            if user:
               
                result = mycollection.update_one({"_id": ObjectId(user["_id"])},{"$set": {"password": password}})
                flash('Changement de mot de passe réussi','success')
                return redirect('/user/change-password')
            else:
                flash('Invalid Email','danger')
                return redirect('/user/change-password')

    else:
        return render_template('user/change-password.html',title="Change Password")

# mise à jour profile utilisateur
@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    user = mycollection.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        # get all input field name
        nom=request.form.get('nom')
        prenom=request.form.get('prenom')
        email=request.form.get('email')
        if nom =="" or prenom=="" or email=="" :
            flash('Veuillez remplir tous les champs','danger')
            return redirect('/user/update-profile')
        else:
            session['username']=None
            mycollection.update_one({"_id": ObjectId(user["_id"])},{"$set": {"nom": nom,"prenom":prenom,"email":email}})
            session['username']=nom + " " +prenom
            flash('Mise à jour réussie du profil','success')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html',title="Update Profile",user=user)






if __name__=="__main__":
    app.run(debug=True)
