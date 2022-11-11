% Frustum unknowns
p = sym('p', [3,1]);
u = sym('u', [3,1]);
syms theta

%input data
t1 = sym('t1', [2,1]);
t2 = sym('t2', [2,1]);
t3 = sym('t3', [2,1]);
x1 = sym('x1', [3,1]);
x2 = sym('x2', [3,1]);
x3 = sym('x3', [3,1]);
syms hfov
syms ar

%extra unknowns for raycast
syms f1 f2 f3

%constants
fwd = [0;0;-1];
up = [0;1;0];
right = [1;0;0];

%preparations
cost = cos(theta);
sint = sin(theta);
mincost = 1-cost;

R = [(cost+u(1)^2*mincost) (u(1)*u(2)*mincost-u(3)*sint) (u(1)*u(3)*mincost+u(2)*sint);
     (u(2)*u(1)*mincost+u(3)*sint) (cost+u(2)^2*mincost) (u(2)*u(3)*mincost-u(1)*sint);
     (u(3)*u(1)*mincost-u(2)*sint) (u(3)*u(2)*mincost+u(1)*sint) (cost+u(3)^2*mincost)];

syms d(t)
t = sym('t', [2,1]);
d(t) = fwd + cos(hfov/2)*right*t(1) + cos(hfov/2)/ar*up*t(2);

d1 = d(t1(1), t1(2));
d2 = d(t2(1), t2(2));
d3 = d(t3(1), t3(2));

%equations
norm = u(1)^2 + u(2)^2 + u(3)^2 - 1;
fid1 = p + f1*R*d1 - x1;
fid2 = p + f2*R*d2 - x2;
fid3 = p + f3*R*d3 - x3;

%function and Jacobian
F = [norm;fid1;fid2;fid3]
vars = [f1, f2, f3, p(1), p(2), p(3), u(1), u(2), u(3), theta]
J = jacobian(F, vars)