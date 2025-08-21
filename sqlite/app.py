import streamlit as st
import pandas as pd
from sqlalchemy import text

# connect to the sqlite database
# streamlit will automatically create the connection details from secrets.toml
conn = st.connection("my_database", type="sql")

# create a table and insert some data (this will only run once)

with conn.session as s:
    # use s.execute to run sql commands
    s.execute(
        text(
            """
              CREATE TABLE IF NOT EXISTS users(
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  age INTEGER
              );
              """
        )
    )

    # cheking if data already exists to avoid duplicates
    existing_users = s.execute(text("SELECT COUNT(*) FROM users;")).scalar()
    if existing_users == 0:
        s.execute(text("INSERT INTO users (name, age) VALUES ('Alice', 30);"))
        s.execute(text("INSERT INTO users (name, age) VALUES ('Bob', 25);"))
        s.execute(text("INSERT INTO users (name, age) VALUES ('Charlie', 35);"))

    # commit the changes to the database
    s.commit()

st.header("User Data")
# query the data and display it in a streamlit dataframe
df = conn.query("SELECT * FROM users;", ttl=0)  # ttl=0 means no caching
st.dataframe(df)

st.divider()

# add a form to insert new data
with st.form("new_user_form", clear_on_submit=True):
    st.subheader("Add New User")
    new_name = st.text_input("Name")
    new_age = st.number_input("Age", min_value=1, max_value=120, step=1)

    submitted = st.form_submit_button("Add User")

    if submitted and new_name:
        try:
            with conn.session as s:
                s.execute(
                    text("INSERT INTO users (name,age) VALUES (:name, :age);"),
                    params={"name": new_name, "age": new_age},
                )
                s.commit()
                st.toast(f"User {new_name} added successfully!", icon="✔️")
                # Return the app to show the updated data
                # st.rerun()
        except Exception as e:
            st.error(f"Error inserting user: {e}")


# # multi-row selection

# df = conn.query("SELECT * FROM users;", ttl=0)  # ttl=0 means no caching
# test = st.dataframe(df.set_index("id"), selection_mode="multi-row", on_select="rerun")

# if test['selection']['rows']:
#     st.subheader(test['selection']['rows'])
#     st.button("Delete Selected Users", key="delete_users")

# st.divider()


# df = conn.query("SELECT * FROM users;", ttl=0)  # ttl=0 means no caching
# df_display = df.set_index("id")
# # st.text(df_display)
# test = st.dataframe(df_display, selection_mode="single-row", on_select="rerun")

# if test["selection"]["rows"]:
#     selected_row_index = test["selection"]["rows"][0]  # Get the selected row index
#     selected_user_id = df.loc[selected_row_index][
#         "id"
#     ]  # Get the selected user ID according to the row index
#     selected_user_name = df.loc[selected_row_index][
#         "name"
#     ]  # Get the selected user name according to the row index

#     print(selected_row_index, selected_user_id, selected_user_name)

#     # Form to delete user by ID
#     with st.form("delete_user_form", clear_on_submit=True):
#         st.subheader("Delete User")
#         delete_id = st.number_input(
#             "Selected User ID", min_value=1, step=1, value=selected_user_id , disabled=True
#         )

#         if st.form_submit_button("Delete User",use_container_width=True, icon="🗑️", help="click to delete user"):
#             try:
#                 with conn.session as s:
#                     result = s.execute(
#                         text("DELETE FROM users WHERE id = :id"),
#                         params={"id": delete_id},
#                     )
#                     s.commit()
#                     st.toast(
#                         f"User with ID {delete_id} deleted successfully!", icon="🗑️"
#                     )
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Error deleting user: {e}")


df = conn.query("SELECT * FROM users;", ttl=0)
df_display = df.set_index("id")
test = st.dataframe(df_display, selection_mode="single-row", on_select="rerun")

# Show toast if stored from previous run
if "toast_message" in st.session_state:
    st.toast(st.session_state.toast_message, icon="🗑️")
    del st.session_state.toast_message  # Clear after showing

if test["selection"]["rows"]:
    selected_row_index = test["selection"]["rows"][0]
    selected_user_id = df.loc[selected_row_index]["id"]
    selected_user_name = df.loc[selected_row_index]["name"]

    with st.form("delete_user_form", clear_on_submit=True):
        st.subheader("Delete User")
        delete_id = st.number_input(
            "Selected User ID",
            min_value=1,
            step=1,
            value=selected_user_id,
            disabled=True,
        )
        ##########################
        st.markdown(
            """
        <style>
        div.stForm button[kind="primary"] {
            background-color: #e74c3c;
            color: white;
        }
        div.stForm button[kind="primary"]:hover {
            background-color: #c0392b;
        }
        </style>
    """,
            unsafe_allow_html=True,
        )
        ############################
        if st.form_submit_button(
            "Delete User",
            use_container_width=True,
            icon="🗑️",
            help="Click to delete user",
            type="primary"
        ):
            try:
                with conn.session as s:
                    s.execute(
                        text("DELETE FROM users WHERE id = :id"),
                        params={"id": delete_id},
                    )
                    s.commit()

                # Store toast message in session state
                st.session_state.toast_message = (
                    f"User with ID {delete_id} deleted successfully!"
                )
                st.rerun()

            except Exception as e:
                st.error(f"Error deleting user: {e}")
