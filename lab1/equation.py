a = int(input('Введите коэффициент a:'))
if a == 0:
    print ('Уравнение не является квадратным')
elif a != 0:
    b = int(input('Введите коэффициент b:'))
    c = int(input('Введите коэффициент c:'))
    if a + b + c == 0:
        print ('x1 = 1', 'x2 = ', c/a)
    elif a + c == b:
        print('x1 = -1', 'x2 = ', -c/a)
    else:
        d = b**2 - 4*a*c;
    if d > 0:
        x1 = (-b - d**0.5)/(2*a)
        x2 = (-b + d**0.5)/(2*a)
        print ('x1 = ', x1, 'x2 = ', x2)
    if d == 0:
        print ('x1 = x2 = ', -b/2*a)
    if d < 0:
        print('Корней нет')
