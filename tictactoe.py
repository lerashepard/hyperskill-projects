def print_board(board):
    print("---------")
    for row in board:
        print("|", end=" ")
        for cell in row:
            print(cell, end=" ")
        print("|")
    print("---------")

def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != " ":
            return f"{row[0]} wins"
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != " ":
            return f"{board[0][col]} wins"
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != " ":
        return f"{board[0][0]} wins"
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != " ":
        return f"{board[0][2]} wins"
    if " " not in [cell for row in board for cell in row]:
        return "Draw"
    return "Game not finished"

def main():
    initial_input = input("Enter the cells: > ")
    board = [[initial_input[i * 3 + j] for j in range(3)] for i in range(3)]
    print_board(board)

    player = "X" if initial_input.count("X") <= initial_input.count("O") else "O"

    while True:
        coords = input("Enter the coordinates: > ").split()
        if len(coords) != 2 or not all(coord.isnumeric() for coord in coords):
            print("You should enter two numbers separated by a space!")
            continue
        x, y = map(int, coords)
        if x < 1 or x > 3 or y < 1 or y > 3:
            print("Coordinates should be from 1 to 3!")
            continue
        if board[3 - y][x - 1] != " ":
            print("This cell is occupied! Choose another one!")
            continue

        board[3 - y][x - 1] = player
        print_board(board)

        result = check_winner(board)
        if result != "Game not finished":
            print(result)
            break

        player = "X" if player == "O" else "O"

if __name__ == "__main__":
    main()

