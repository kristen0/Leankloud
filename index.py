from flask import Flask
from flask_restx import Api, Resource, fields,inputs
from pandas import cut
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3

 
# table = """ create table todo (
#             id integer primary key autoincrement not null,
#             task text not null,
#             due_by text not null,
#             status text not null
#         ); """

# cursor.execute(table)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by': fields.Date(required=True, description='When this task should be finished'),
    'status': fields.String(required=True, description='status of task not started, in progress, and finished')
})


class TodoDAO(object):


    def todo(self):
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            todos = []
            q = f"select * from todo"
            cursor.execute(q)
            output = cursor.fetchall()
            for row in output:
                todos.append({'id':row[0],'task':row[1],'due_by':row[2],'status':row[3]})
            return todos

    def get(self, id):
        with sqlite3.connect("data.db") as conn:
            cursor  = conn.cursor()
            q = f"select * from todo where id = {id}"
            cursor.execute(q)
            output = cursor.fetchall()
            if len(output) == 0:
                api.abort(404, "Todo {} doesn't exist".format(id))
            return {'id':id,'task':output[0][1],'due_by':output[0][2],'status':output[0][3]}

    def create(self, data):
        with sqlite3.connect("data.db") as conn:
            cursor  = conn.cursor()
            q = f"insert into todo (task, due_by, status ) values ('{data['task']}', '{data['due_by']}', '{data['status']}')"
            cursor.execute(q)
            id = cursor.lastrowid
            conn.commit()
            return {'id':id,'task':data['task'],'due_by':data['due_by'],'status':data['status']}

    def update(self, id, data):
        with sqlite3.connect("data.db") as conn:
            cursor  = conn.cursor()
            q = f"select id from todo where id = {id}"
            cursor.execute(q)
            output = cursor.fetchall()
            if len(output) == 0:
                api.abort(404, "Todo {} doesn't exist".format(id))
            q = f"update todo set task = '{data['task']}', due_by = '{data['due_by']}', status = '{data['status']}' where id = {id};"
            cursor.execute(q)
            conn.commit()
            return {'id':id,'task':data['task'],'due_by':data['due_by'],'status':data['status']}

    def delete(self, id):
        with sqlite3.connect("data.db") as conn:
            cursor  = conn.cursor()
            q = f"select id from todo where id = {id}"
            cursor.execute(q)
            output = cursor.fetchall()
            if len(output) == 0:
                api.abort(404, "Todo {} doesn't exist".format(id))
            q = f"delete from todo where id = {id}"
            cursor.execute(q)
            conn.commit()
            return
    def due(self,due):
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            todos = []
            q = f"select * from todo where due_by = '{due}'"
            cursor.execute(q)
            output = cursor.fetchall()
            for row in output:
                todos.append({'id':row[0],'task':row[1],'due_by':row[2],'status':row[3]})
            return todos
    
    def overdue(self):
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            todos = []
            q = f"select * from todo where date('now') > due_by"
            cursor.execute(q)
            output = cursor.fetchall()
            for row in output:
                todos.append({'id':row[0],'task':row[1],'due_by':row[2],'status':row[3]})
            return todos
    
    def finished(self):
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            todos = []
            q = f"select * from todo where status = 'finished'"
            cursor.execute(q)
            output = cursor.fetchall()
            for row in output:
                todos.append({'id':row[0],'task':row[1],'due_by':row[2],'status':row[3]})
            return todos


DAO = TodoDAO()



@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.todo()

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

parser = ns.parser()
parser.add_argument('due_date', type=inputs.date_from_iso8601, help='due date')

@ns.route('/due')
class TodoDue(Resource):
    @ns.expect(parser)
    @ns.marshal_list_with(todo)
    def get(self):
        '''Gets all todos with the given due date'''
        return DAO.due(parser.parse_args()["due_date"])

@ns.route('/overdue')
class TodoOverdue(Resource):
    @ns.marshal_list_with(todo)
    def get(self):
        '''Gets all todos which are overdue'''
        return DAO.overdue()

@ns.route('/finished')
class TodoFinished(Resource):
    @ns.marshal_list_with(todo)
    def get(self):
        '''Gets all todos with status finished'''
        return DAO.finished()

if __name__ == '__main__':
    app.run(debug=True)