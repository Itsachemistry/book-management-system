import click
from flask.cli import with_appcontext
from .models.user import User
from . import db

@click.command('init-admin')
@click.option('--username', default='admin', help='Admin username')
@click.option('--password', default='admin123', help='Admin password')
@click.option('--employee-id', default='EMP001', help='Admin employee ID')
@with_appcontext
def init_admin_command(username, password, employee_id):
    """创建超级管理员用户"""
    # 检查是否已存在
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo(f'用户 {username} 已存在')
        return
    
    # 创建超级管理员
    admin = User(
        username=username,
        employee_id=employee_id,
        full_name='System Administrator',
        role='SUPER_ADMIN'
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    click.echo(f'超级管理员 {username} 创建成功')

# 在__init__.py的create_app函数中注册此命令
def register_commands(app):
    app.cli.add_command(init_admin_command)