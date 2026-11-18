from dataclasses import dataclass

from bakery import assert_equal
from drafter import *


@dataclass
class PianoPiece:
    """Represents a single piano song in the student's repertoire.

    Attributes:
        title (str): The name of the musical piece.
        composer (str): The composer who wrote the piece.
        difficulty (str): Skill level ('Beginner', 'Intermediate', 'Advanced').
        minutes_practiced (int): Cumulative practice time in minutes.
        is_mastered (bool): Whether the student has mastered the piece.
    """
    title: str
    composer: str
    difficulty: str
    minutes_practiced: int
    is_mastered: bool

@dataclass
class State:
    """Stores global application state for the piano studio.

    Attributes:
        pieces (list[PianoPiece]): The user's repertoire list.
        weekly_goal_minutes (int): Target practice minutes per week.
        filter_difficulty (str): Active difficulty level filter.
        logged_sessions (int): Total number of practice sessions logged.
    """
    pieces: list[PianoPiece]
    weekly_goal_minutes: int
    filter_difficulty: str
    logged_sessions: int

def initial_state() -> State:
    """ Creates and returns the initial state with the starter repertoire
    
    """

    starter_pieces = [
    PianoPiece("Für Elise", "Beethoven", "Intermediate", 120, True),
    PianoPiece("Clair de Lune", "Debussy", "Advanced", 45, False),
    PianoPiece("Minuet in G", "Bach", "Beginner", 90, True),
]

    return State(
        pieces=starter_pieces,
        weekly_goal_minutes=150,
        filter_difficulty="All",
        logged_sessions=3
    )

def calculate_total_practice_time(pieces: list[PianoPiece]) -> int:
    """Calculates total practice minutes across all pieces in a list.

    Args:
        pieces (list[PianoPiece]): A list of PianoPiece instances.

    Returns:
        int: The sum of minutes_practiced across all pieces.
    """
    # List comprehension extracts minutes_practiced from each PianoPiece
    return sum([piece.minutes_practiced for piece in pieces])

def count_mastered_pieces(pieces: list[PianoPiece]) -> int:
    """Counts how many pieces in the repertoire are marked as mastered.

    Args:
        pieces (list[PianoPiece]): A list of PianoPiece instances.

    Returns:
        int: The total number of pieces where is_mastered is True.
    """
    # List comprehension filters for pieces where is_mastered is True
    return len([piece for piece in pieces if piece.is_mastered])

def format_piece_line(piece: PianoPiece) -> Text:
    """Formats a single PianoPiece into a Drafter Text component.

    Args:
        piece (PianoPiece): The piano piece to format.

    Returns:
        Text: A Drafter Text element summarizing the piece details.
    """

    status_tag = "Mastered" if piece.is_mastered else "In Progress"
    return Text(
        f"{piece.title} ({piece.composer}) - {piece.difficulty} | "
        f"{piece.minutes_practiced} mins | {status_tag}"
    )


@route
def index(state: State) -> Page:
    """Renders the main piano studio dashboard page.

    Args:
        state (State): The current global application state.

    Returns:
        Page: The rendered home dashboard page showing stats and pieces.
    """

    total_time = calculate_total_practice_time(state.pieces)
    mastered_count = count_mastered_pieces(state.pieces)

    if total_time >= state.weekly_goal_minutes:
        goal_status = "Weekly practice goal achieved!"
    else:
        remaining = state.weekly_goal_minutes - total_time
        goal_status = f"{remaining} more minutes to reach weekly goal."

    header_content = [
      Header("Piano Practice Tracker Dashboard"),
        Text(f"Repertoire Count: {len(state.pieces)} pieces | "),
        Text(f"Mastered Pieces: {mastered_count} | "),
        Text(f"Total Practice Time: {total_time} minutes"),
        LineBreak(),
        Text(goal_status),
        LineBreak(),
        LineBreak(),
        Button("Add New Song", add_piece_page),
        Button("Log Practice", log_practice_page),
        Button("Filter Repertoire", filtered_repertoire),
        Button("Set Weekly Goal", goal_page),
        Button("Theory Quiz", theory_quiz),
        LineBreak(),
        LineBreak(),
    ]

    # List comprehension converts each PianoPiece into a Drafter Text element
    piece_elements = [element
        for piece in state.pieces
        for element in (format_piece_line(piece), LineBreak())]

    return Page(state, header_content + piece_elements)

@route
def add_piece_page(state: State) -> Page:
    """Renders the form page for adding a new piano piece.

    Args:
        state (State): The current global application state.

    Returns:
        Page: The rendered page containing input fields for a new song.
    """

    return Page(state, [
        Header("Add New Song to Repertoire"),
        TextBox("title_in", "Song Title"),
        TextBox("composer_in", "Composer Name"),
        SelectBox("diff_in", ["Beginner", "Intermediate", "Advanced"]),
        Text("Already Mastered?"),
        CheckBox("mastered_in", False),
        Button("Save Piece", save_piece),
        Button("Cancel / Back", index)
    ])


@route
def save_piece(state: State, title_in: str, composer_in: str,
               diff_in: str, mastered_in: bool) -> Page:

    
    """Validates form inputs and appends a new PianoPiece to state.

    Args:
        state (State): The current global application state.
        title_in (str): The title entered by the user.
        composer_in (str): The composer name entered by the user.
        diff_in (str): The selected difficulty level.
        mastered_in (bool): Whether the song is already mastered.

    Returns:
        Page: Redirects to the updated home dashboard page.
    """

    if title_in.strip() != "" and composer_in.strip() != "":
        new_piece = PianoPiece(
            title = title_in.strip(),
            composer = composer_in.strip(),
            difficulty=diff_in,
            minutes_practiced=0,
            is_mastered=mastered_in
        )
        state.pieces.append(new_piece)

    return index(state)

@route
def log_practice_page(state: State) -> Page:
    """Renders the form page for logging a piano practice session.

    Args:
        state (State): The current global application state.

    Returns:
        Page: The rendered page with dropdowns for song and duration.
    """

    # List comprehension builds a list of song title strings for the SelectBox
    song_titles = [piece.title for piece in state.pieces]
    if not song_titles:
        song_titles = ["No songs available"]

    return Page(state, [
        Header("Log Piano Practice Session"),
        SelectBox("selected_song", song_titles),
        SelectBox("minutes_spent", ["15", "30", "45", "60", "90"]),
        Button("Submit Session", save_practice),
        Button("Back to Dashboard", index)
    ])

@route
def save_practice(state: State, selected_song: str,
                  minutes_spent: str) -> Page:

    """Updates practice minutes for the selected piece and increments sessions.

    Args:
        state (State): The current global application state.
        selected_song (str): The title of the song practiced.
        minutes_spent (str): The number of minutes practiced as a string.

    Returns:
        Page: Redirects to the updated home dashboard page.
    """

    added_mins = int(minutes_spent)

    for piece in state.pieces:
        if piece.title == selected_song:
            piece.minutes_practiced += added_mins

    state.logged_sessions += 1
    return index(state)

@route
def filtered_repertoire(state: State) -> Page:
    """Renders the repertoire page filtered by the active difficulty level.

    Args:
        state (State): The current global application state.

    Returns:
        Page: The rendered page showing songs matching filter_difficulty.
    """

    controls = [
        Header("Filter Repertoire by Difficulty"),
        SelectBox(
            "level_filter",
            ["All", "Beginner", "Intermediate", "Advanced"]
        ),
        Button("Apply Filter", set_difficulty_filter),
        Button("Back to Dashboard", index)
    ]

    # List comprehension filters pieces matching filter_difficulty into Text
    matching_elements = [
      element
      for piece in state.pieces
      if state.filter_difficulty == "All"
      or piece.difficulty == state.filter_difficulty
      for element in (
          Text(f"{piece.title} - Level: {piece.difficulty}"),
          LineBreak(),
      )
  ]

    return Page(state, controls + matching_elements)

@route
def goal_page(state: State) -> Page:
    """Renders the form page for updating the weekly practice goal.

    Args:
        state (State): The current global application state.

    Returns:
        Page: The rendered page with an input box for weekly goal minutes.
    """

    return Page(state, [
        Header("Set Weekly Practice Goal"),
        Text(f"Current Weekly Goal: {state.weekly_goal_minutes} minutes"),
        LineBreak(),
        TextBox("goal_in", str(state.weekly_goal_minutes)),
        Button("Save Goal", update_goal),
        Button("Back to Dashboard", index)
    ])

@route
def update_goal(state: State, goal_in: str) -> Page:
    """Updates the weekly practice goal in the application state.

    Args:
        state (State): The current global application state.
        goal_in (str): The new weekly goal in minutes entered by the user.

    Returns:
        Page: Redirects to the updated goal_page.
    """

    state.weekly_goal_minutes = int(goal_in.strip())
    return index(state)

@route
def set_difficulty_filter(state: State, level_filter: str) -> Page:
    """Updates the active difficulty filter in the application state.

    Args:
        state (State): The current global application state.
        level_filter (str): The difficulty level selected by the user.

    Returns:
        Page: Redirects to the updated filtered_repertoire page.
    """

    state.filter_difficulty = level_filter
    return filtered_repertoire(state)

@route
def theory_quiz(state: State) -> Page:
    """Renders the piano music theory multiple-choice quiz page.

    Args:
        state (State): The current global application state.

    Returns:
        Page: The rendered quiz question page.
    """

    question = (
        "Question: Which key sists directly to the left of the two black keys?"
    )

    return Page(state, [
        Header("Piano Music Theory Quiz"),
        Text(question),
        SelectBox(
            "user_answer",
            ["Key of C", "Key of F", "Key of B", "Key of G"]
        ),
        Button("Check Answer", evaluate_quiz),
        Button("Back to Dashboard", index)
    ])

@route
def evaluate_quiz(state: State, user_answer: str) -> Page:
    """Evaluates the user's quiz selection and displays result feedback.

    Args:
        state (State): The current global application state.
        user_answer (str): The option chosen by the user.

    Returns:
        Page: The rendered quiz result page with feedback text.
    """

    if user_answer == "Key of C":
        feedback = (
            "Correct! Middle C sits directly before the pair of black keys."
        )
    else:
        feedback = "Incorrect! Try again."

    return Page(state, [
        Header("Quiz Result"),
        Text(feedback),
        Button("Try Again", theory_quiz),
        Button("Return Home", index)
    ])


assert_equal(calculate_total_practice_time([]), 0)
assert_equal(
    calculate_total_practice_time([
        PianoPiece("Für Elise", "Beethoven", "Intermediate", 120, True),
        PianoPiece("Clair de Lune", "Debussy", "Advanced", 45, False),
    ]),
    165,
)

assert_equal(count_mastered_pieces([]), 0)
assert_equal(
    count_mastered_pieces([
        PianoPiece("Für Elise", "Beethoven", "Intermediate", 120, True),
        PianoPiece("Clair de Lune", "Debussy", "Advanced", 45, False),
    ]),
    1,
)

assert_equal(
    format_piece_line(
        PianoPiece("Für Elise", "Beethoven", "Intermediate", 120, True)
    ),
    Text("Für Elise (Beethoven) - Intermediate | 120 mins | Mastered"),
)
assert_equal(
    format_piece_line(
        PianoPiece("Clair de Lune", "Debussy", "Advanced", 45, False)
    ),
    Text("Clair de Lune (Debussy) - Advanced | 45 mins | In Progress"),
)

# --- Route Tests ---
# index route
test_state_index = initial_state()
index_page = index(test_state_index)
assert_equal(index_page.state, test_state_index)
assert_equal(index_page.content[0], Header("Piano Practice Tracker Dashboard"))

# add_piece_page route
test_state_add = initial_state()
add_page = add_piece_page(test_state_add)
assert_equal(add_page.state, test_state_add)
assert_equal(len(add_page.content) > 0, True)

# save_piece route
test_state_save = initial_state()
save_page = save_piece(
    test_state_save, "Minuet in G", "Bach", "Beginner", True
)
assert_equal(save_page.state, test_state_save)
assert_equal(len(test_state_save.pieces), 4)
assert_equal(
    test_state_save.pieces[-1],
    PianoPiece("Minuet in G", "Bach", "Beginner", 0, True),
)

# log_practice_page route
test_state_log_page = initial_state()
log_page = log_practice_page(test_state_log_page)
assert_equal(log_page.state, test_state_log_page)
assert_equal(len(log_page.content) > 0, True)

# save_practice route
test_state_log = initial_state()
logged_page = save_practice(test_state_log, "Clair de Lune", "35")
assert_equal(logged_page.state, test_state_log)
assert_equal(test_state_log.pieces[1].minutes_practiced, 80)
assert_equal(test_state_log.pieces[1].is_mastered, False)

# filtered_repertoire route
test_state_filtered = initial_state()
filtered_page = filtered_repertoire(test_state_filtered)
assert_equal(filtered_page.state, test_state_filtered)
assert_equal(len(filtered_page.content) > 0, True)

# goal_page route
test_state_goal_page = initial_state()
g_page = goal_page(test_state_goal_page)
assert_equal(g_page.state, test_state_goal_page)
assert_equal(g_page.content[0], Header("Set Weekly Practice Goal"))

# update_goal route
test_state_goal = initial_state()
updated_goal_page = update_goal(test_state_goal, "300")
assert_equal(updated_goal_page.state, test_state_goal)
assert_equal(test_state_goal.weekly_goal_minutes, 300)

# set_difficulty_filter route
test_state_filter = initial_state()
filter_page = set_difficulty_filter(test_state_filter, "Advanced")
assert_equal(filter_page.state, test_state_filter)
assert_equal(test_state_filter.filter_difficulty, "Advanced")

# theory_quiz route
test_state_theory = initial_state()
theory_page = theory_quiz(test_state_theory)
assert_equal(theory_page.state, test_state_theory)
assert_equal(theory_page.content[0], Header("Piano Music Theory Quiz"))

# evaluate_quiz route
test_state_quiz = initial_state()
assert_equal(
    evaluate_quiz(test_state_quiz, "Key of C").content[1],
    Text("Correct! Middle C sits directly before the pair of black keys."),
)
assert_equal(
    evaluate_quiz(test_state_quiz, "Key of G").content[1],
    Text("Incorrect! Try again."),
)

set_site_information(
    author="Eehan Masud",
    description=(
        "A virtual piano studio web app to manage repertoire, "
        "track practice goals, and test music theory."
    ),
    sources= ["Copy of CS1 Final Project 0_ Pick a Problem.docx", "Copy of CS1 Final Project 1_ Design.docx", "LLM Conversation.docx"],
    planning= ["Copy of CS1 Final Project 0_ Pick a Problem.docx", "Copy of CS1 Final Project 1_ Design.docx"],
    links="https://github.com/eehanmasud/Piano_Tracker_Site",
)

start_server(initial_state())
