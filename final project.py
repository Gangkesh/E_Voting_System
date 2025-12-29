import turtle
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pushbullet import Pushbullet
import pyautogui,os
import time,csv,sys
from pathlib import Path




BASE_DIR = Path(__file__).parent / "VotingData"
VOTER_FILE = BASE_DIR / "voter.csv"
CANDIDATE_FILE = BASE_DIR / "candidate.csv"


background_img = BASE_DIR / "background.jpg"
review_path = BASE_DIR / "review.txt"

admin_login_key=[0,123456789012,123456] 
voting_going=False
api_key='' 
idle_bg_color="#002240" 


i=0
k=[]
window = None 
main_frame = None  
input_frame1 = None 


user_id = None
aadhar_number = None


logged_in_voter_id = None
logged_in_aadhar_number = None



def update_candidate_vote(candidate_id_to_vote_for):
    """Reads candidate data, increments vote count for the given ID, and writes back."""
    global CANDIDATE_FILE
    candidate_data = []
    vote_recorded = False

    try:
        with open(CANDIDATE_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            candidate_data = list(reader)
    except FileNotFoundError:
        pyautogui.alert('Candidate file not found! Check the VotingData folder.')
        return False
    except Exception as e:
        pyautogui.alert(f'Error reading candidate file: {e}')
        return False

    new_candidate_data = []
    
    for row in candidate_data:
        if len(row) == 0:
            continue
            
     
        if row[0].lower() != 'candidate_id' and len(row) < 6:
            row.append('0') 
        elif row[0].lower() == 'candidate_id' and len(row) == 5:
            row.append('votes')         
        
        if row[0] == candidate_id_to_vote_for:
            try:
                # Get the current vote count (index 5)
                current_votes = int(row[5])
                row[5] = str(current_votes + 1) # Increment and convert back to string
                vote_recorded = True
            except (ValueError, IndexError):
                # Handles corrupted/missing vote count data
                if row[0].lower() != 'candidate_id':
                    row[5] = '1' # Set to 1 if previously corrupt/empty
                    vote_recorded = True
            
        new_candidate_data.append(row)

    if vote_recorded:
        try:
            with open(CANDIDATE_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(new_candidate_data)
            return True
        except Exception as e:
            pyautogui.alert(f'Error writing back to candidate file: {e}')
            return False
    else:
        if candidate_id_to_vote_for.lower() != 'candidate_id':
            pyautogui.alert('Candidate ID not found in the list.')
        return False
        
def mark_voter_as_voted(voter_id_current):
    """Updates the voter CSV file to set the 'voted' status to 'True'."""
    global VOTER_FILE
    voter_data = []
    try:
        with open(VOTER_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            voter_data = list(reader)
    except FileNotFoundError:
        pyautogui.alert('Voter file not found! Check the VotingData folder.')
        return

    new_voter_data = []
    voter_found_and_marked = False

    for row in voter_data:
        if row and row[0].lower() == 'voter_id':
            new_voter_data.append(row)
            continue
            
        if len(row) >= 5 and row[0] == voter_id_current:
            if row[4].lower() == 'false':
                row[4] = 'True'
                voter_found_and_marked = True
        new_voter_data.append(row)

    if voter_found_and_marked:
        with open(VOTER_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(new_voter_data)

# --- TKINTER APP DEFINITION ---

def app():
    global idle_bg_color, background_img, window
    window=tk.Tk()
    window.title('Voting System')
    window.geometry('1366x718')
    
    # Load and setup background image
    try:
        bg = Image.open(background_img) 
        bg = bg.resize((1366, 768), Image.Resampling.LANCZOS)
        bg_img = ImageTk.PhotoImage(bg)
        bg_label = tk.Label(window, image=bg_img)
        bg_label.place(relwidth=1, relheight=1)
        bg_label.image = bg_img 
    except Exception as e:
        print(f"Warning: Could not load background image: {e}")
        window.config(bg=idle_bg_color)
    
    # Define menu state holders
    title = tk.Label()
    input_frame = tk.Frame()
    
    # ----------------------------------------------------
    # All Function definitions 
    # ----------------------------------------------------

    # --- MAIN MENU NAVIGATION ---
    
    def go_to_main_menu():
        global title,input_frame, main_frame, input_frame1
        try:
            title.destroy()
            if input_frame: input_frame.destroy()
            if main_frame: 
                main_frame.destroy()
                main_frame = None
            if input_frame1:
                input_frame1.destroy()
                input_frame1 = None
        except:
            pass
        main_menu()
        
    def main_menu():
        global title,input_frame
        
        title=tk.Label(master=window,text='Welcome To Voting System',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=50)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        admin_login_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Admin Login',command=admin_login, width=15)
        admin_login_btn.grid(row=1,column=0,padx=15,pady=10)
        
        voter_login_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Voter Login',command=voter_login, width=15)
        voter_login_btn.grid(row=1,column=1,padx=15,pady=10)
        
        candidate_login_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Candidate Area',command=candidate_login, width=15)
        candidate_login_btn.grid(row=1,column=2,padx=15,pady=10)
        
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Exit',command=window.destroy, width=10)
        exit_btn.grid(row=2,column=1,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        
    # --- ADMIN FUNCTIONS ---
    
    def submit_enter_voter_details():
        global user_id,user_name,user_age,aadhar_number, VOTER_FILE
        try:
            with open(VOTER_FILE,'a',newline='') as f:
                k=[user_id.get(),user_name.get(),user_age.get(),aadhar_number.get(),'False'] 
                m=csv.writer(f)
                m.writerow(k)
            pyautogui.alert('Submitted Voter Data Successfully')
        except Exception as e:
            pyautogui.alert(f'Error writing to voter file: {e}')

    def enter_voter_details_menu():
        global title,input_frame,user_id,user_name,user_age,aadhar_number
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Enter Voter Details',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        user_id_title=tk.Label(master=input_frame,text='Voter Id:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        user_id_title.grid(row=1,column=0,padx=15,pady=10, sticky='w')
        user_id=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        user_id.grid(row=1,column=1,padx=15,pady=10, sticky='ew')
        
        user_name_title=tk.Label(master=input_frame,text='Voter Name:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        user_name_title.grid(row=2,column=0,padx=15,pady=10, sticky='w')
        user_name=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        user_name.grid(row=2,column=1,padx=15,pady=10, sticky='ew')
        
        user_age_title=tk.Label(master=input_frame,text='Voter Age:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        user_age_title.grid(row=3,column=0,padx=15,pady=10, sticky='w')
        user_age=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        user_age.grid(row=3,column=1,padx=15,pady=10, sticky='ew')
        
        aadhar_number_title=tk.Label(master=input_frame,text='Aadhar Number:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        aadhar_number_title.grid(row=4,column=0,padx=15,pady=10, sticky='w')
        aadhar_number=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        aadhar_number.grid(row=4,column=1,padx=15,pady=10, sticky='ew')

        def enter_voter_details_check():
            if not (user_age.get().isdigit() and aadhar_number.get().isdigit() and user_id.get().isdigit()):
                pyautogui.alert('Error: ID, Age, and Aadhar must be numeric.')
                return
            if not user_name.get().replace(' ', '').isalpha():
                pyautogui.alert('Error: Voter Name must contain only letters.')
                return
            if len(aadhar_number.get())!=12:
                pyautogui.alert('Error: Aadhar Number must be exactly 12 digits.')
                return
            
            age = int(user_age.get())
            if age < 18:
                pyautogui.alert('Voter must be 18 years old.')
                admin_menu()
                return
            
            submit_enter_voter_details()
                
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=admin_menu, width=10)
        exit_btn.grid(row=5,column=0,padx=15,pady=20)
        submit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Submit',command=enter_voter_details_check, width=10)
        submit_btn.grid(row=5,column=1,padx=15,pady=20)
        
        input_frame.pack(pady=10)
        
    def submit_enter_candidate_details():
        global candidate_id,candidate_name,candidate_age,candidate_aadhar_number,candidate_motto, CANDIDATE_FILE
        try:
            with open(CANDIDATE_FILE,'a', newline='') as f:
                # Appending '0' as the initial vote count (index 5)
                k=[candidate_id.get(),candidate_name.get(),candidate_age.get(),candidate_aadhar_number.get(),candidate_motto.get(), '0']
                m=csv.writer(f)
                m.writerow(k)
            pyautogui.alert('Submitted Candidate Data Successfully')
        except Exception as e:
            pyautogui.alert(f'Error writing to candidate file: {e}')

    def enter_candidate_details():
        global title,input_frame,candidate_id,candidate_name,candidate_age,candidate_aadhar_number,candidate_motto
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Enter Candidate details',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        candidate_id_title=tk.Label(master=input_frame,text='Candidate Id:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_id_title.grid(row=1,column=0,padx=15,pady=10, sticky='w')
        candidate_id=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        candidate_id.grid(row=1,column=1,padx=15,pady=10, sticky='ew')
        
        candidate_name_title=tk.Label(master=input_frame,text='Candiate Name:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_name_title.grid(row=2,column=0,padx=15,pady=10, sticky='w')
        candidate_name=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        candidate_name.grid(row=2,column=1,padx=15,pady=10, sticky='ew')
        
        candidate_age_title=tk.Label(master=input_frame,text='Candidate Age:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_age_title.grid(row=3,column=0,padx=15,pady=10, sticky='w')
        candidate_age=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        candidate_age.grid(row=3,column=1,padx=15,pady=10, sticky='ew')
        
        candidate_aadhar_number_title=tk.Label(master=input_frame,text='Aadhar Number:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_aadhar_number_title.grid(row=4,column=0,padx=15,pady=10, sticky='w')
        candidate_aadhar_number=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        candidate_aadhar_number.grid(row=4,column=1,padx=15,pady=10, sticky='ew')
        
        candidate_motto_title=tk.Label(master=input_frame,text="Candidate's Motto:",font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_motto_title.grid(row=5,column=0,padx=15,pady=10, sticky='w')
        candidate_motto=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        candidate_motto.grid(row=5,column=1,padx=15,pady=10, sticky='ew')
        
        def enter_candidate_details_check():
            global candidate_id,candidate_name,candidate_age,candidate_aadhar_number,candidate_motto
            
            if not (candidate_age.get().isdigit() and candidate_aadhar_number.get().isdigit() and candidate_id.get().isdigit()):
                pyautogui.alert('Error: ID, Age, and Aadhar must be numeric.')
                return
            if not candidate_name.get().replace(' ', '').isalpha():
                pyautogui.alert('Error: Candidate Name must contain only letters.')
                return
            if len(candidate_aadhar_number.get())!=12:
                pyautogui.alert('Error: Aadhar Number must be exactly 12 digits.')
                return
            
            age = int(candidate_age.get())
            if age < 20:
                pyautogui.alert('Candidate must be at least 20 years old.')
                admin_menu()
                return

            submit_enter_candidate_details()
                
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=admin_menu, width=10)
        exit_btn.grid(row=6,column=0,padx=15,pady=20)
        submit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Submit',command=enter_candidate_details_check, width=10)
        submit_btn.grid(row=6,column=1,padx=15,pady=20)
        
        input_frame.pack(pady=10)
        
    def start_voting():
        global title, input_frame, api_key, voting_going
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Start Voting',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        k='Voting Is Going On' if voting_going else 'Voting Is Stopped'
        voting_going_title=tk.Label(master=input_frame,text=k,font='Calibri 24 bold',bg=idle_bg_color,fg='white')
        voting_going_title.grid(row=3,column=0,columnspan=2,padx=15,pady=20)

        def start_voting_logic():
            nonlocal voting_going_title 
            global voting_going 
            
            if voting_going==True:
                pyautogui.alert('Voting is already going on')
            else:
                pyautogui.alert('Voting Has Been officially Started. Press Notify to Inform the Voters.')
                voting_going=True
            
            k='Voting Is Going On' if voting_going else 'Voting Is Stopped'
            voting_going_title.config(text=k)
            
        def start_notify():
            global api_key
            if not api_key:
                pyautogui.alert("Pushbullet API Key is missing. Notification aborted.")
                return
            try:
                pb=Pushbullet(api_key)
                pb.push_note('Voting System Update','Voting Has Begun! Cast Your Vote Today.')
                pyautogui.alert('Voters have been successfully notified.')
            except Exception as e:
                pyautogui.alert(f'Notification failed: {e}. Check your API key and internet connection.')

        start_voting_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Start Voting',command=start_voting_logic, width=15)
        start_voting_btn.grid(row=1,column=0,padx=15,pady=10)
        notify_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Notify others',command=start_notify, width=15)
        notify_btn.grid(row=1,column=1,padx=15,pady=10)
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=admin_menu, width=10)
        exit_btn.grid(row=5,column=0,columnspan=2,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        
    def stop_voting():
        global title, input_frame, api_key, voting_going
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Stop Voting',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        k='Voting Is Going On' if voting_going else 'Voting Is Stopped'
        voting_going_title=tk.Label(master=input_frame,text=k,font='Calibri 24 bold',bg=idle_bg_color,fg='white')
        voting_going_title.grid(row=3,column=0,columnspan=2,padx=15,pady=20)
        
        def stop_voting_logic():
            nonlocal voting_going_title 
            global voting_going 
            
            if voting_going==False:
                pyautogui.alert('Voting is already ended')
            else:
                pyautogui.alert('Voting Has Been officially Ended. Press Notify to Inform the Voters.')
                voting_going=False
            
            k='Voting Is Going On' if voting_going else 'Voting Is Stopped'
            voting_going_title.config(text=k)

        def stop_notify():
            global api_key
            if not api_key:
                pyautogui.alert("Pushbullet API Key is missing. Notification aborted.")
                return
            try:
                pb=Pushbullet(api_key)
                pb.push_note('Voting System Update','Voting has Ended! See The Results Today.')
                pyautogui.alert('Voters have been successfully notified.')
            except Exception as e:
                pyautogui.alert(f'Notification failed: {e}. Check your API key and internet connection.')

        stop_voting_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Stop Voting',command=stop_voting_logic, width=15)
        stop_voting_btn.grid(row=1,column=0,padx=15,pady=10)
        notify_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Notify others',command=stop_notify, width=15)
        notify_btn.grid(row=1,column=1,padx=15,pady=10)
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=admin_menu, width=10)
        exit_btn.grid(row=5,column=0,columnspan=2,padx=15,pady=10)
        
        input_frame.pack(pady=10)

    # --- OLD, LESS ROBUST VIEW_CURRENT_POLL (Kept as per previous instruction) ---
    def view_current_poll():
        global title, input_frame, window, idle_bg_color, main_frame
        
        title.destroy()
        input_frame.destroy()
        
        title=tk.Label(master=window,text='📊 Current Poll Results',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        main_frame = tk.Frame(master=window, bg=idle_bg_color)
        main_frame.pack(pady=10, padx=20, fill='x')

        tree = ttk.Treeview(main_frame, columns=('ID', 'Name', 'Motto', 'Votes'), show='headings')
        tree.heading('ID', text='ID', anchor='center')
        tree.heading('Name', text='Candidate Name', anchor='center')
        tree.heading('Motto', text='Motto', anchor='center')
        tree.heading('Votes', text='Vote Count', anchor='center')
        
        tree.column('ID', width=50, anchor='center')
        tree.column('Name', width=200, anchor='w')
        tree.column('Motto', width=350, anchor='w')
        tree.column('Votes', width=100, anchor='center')
        
        candidate_data = []
        try:
            with open(CANDIDATE_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header row
                for row in reader:
                    if len(row) >= 6:
                        candidate_data.append(row)
        except FileNotFoundError:
            pyautogui.alert('Candidate file not found!')
            return

        # THIS SORTING IS THE LESS ROBUST PART:
        # It relies heavily on index 5 existing and being a valid integer string.
        candidate_data.sort(key=lambda x: int(x[5]) if len(x)>5 and x[5].isdigit() else 0, reverse=True)
        
        for record in candidate_data:
            vote_count = record[5] if len(record) > 5 else '0'
            tree.insert('', tk.END, values=(record[0], record[1], record[4], vote_count))
            
        tree.pack(fill='both', expand=True)

        def destroy_poll_view():
            title.destroy()
            input_frame.destroy()
            main_frame.destroy()
            admin_menu()

        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=destroy_poll_view)
        exit_btn.pack(padx=15,pady=10)
        input_frame.pack(pady=10)
        
    def voted_or_not():
        global title, input_frame, window, idle_bg_color, main_frame
        
        title.destroy()
        input_frame.destroy()
        
        title=tk.Label(master=window,text='✅ Voted and ❌ Not Voted List',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        main_frame = tk.Frame(master=window, bg=idle_bg_color)
        main_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        voted_frame = tk.Frame(notebook, bg="white")
        not_voted_frame = tk.Frame(notebook, bg="white")
        
        notebook.add(voted_frame, text=" Voters Who Voted ")
        notebook.add(not_voted_frame, text=" Voters Who Haven't Voted ")
        
        voted_list = []
        not_voted_list = []
        
        try:
            with open(VOTER_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header row
                for row in reader:
                    if len(row) >= 5:
                        voter_info = (row[0], row[1], row[3]) 
                        if row[4].lower() == 'true':
                            voted_list.append(voter_info)
                        else:
                            not_voted_list.append(voter_info)
        except FileNotFoundError:
            pyautogui.alert('Voter data file not found!')
            
        def setup_voter_table(parent_frame, data_list):
            tree = ttk.Treeview(parent_frame, columns=('ID', 'Name', 'Aadhar'), show='headings')
            
            tree.heading('ID', text='ID', anchor='center')
            tree.heading('Name', text='Voter Name', anchor='center')
            tree.heading('Aadhar', text='Aadhar Number', anchor='center')
            
            tree.column('ID', width=100, anchor='center')
            tree.column('Name', width=200, anchor='w')
            tree.column('Aadhar', width=250, anchor='center')
            
            for voter in data_list:
                tree.insert('', tk.END, values=voter)
                
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
        setup_voter_table(voted_frame, voted_list)
        setup_voter_table(not_voted_frame, not_voted_list)
        
        def destroy_voter_list_view():
            title.destroy()
            input_frame.destroy()
            main_frame.destroy()
            admin_menu()

        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=destroy_voter_list_view)
        exit_btn.pack(padx=15,pady=10)
        input_frame.pack(pady=10)
        
    def data_eraser():
        global title,input_frame
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Data Eraser (Not Implemented)',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack()
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        eraser_note = tk.Label(master=input_frame, text="This feature allows you to reset voter and candidate data.", 
                               font='Calibri 18', bg=idle_bg_color, fg='yellow')
        eraser_note.grid(row=0, column=0, columnspan=2, padx=15, pady=20)
        
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=admin_menu)
        exit_btn.grid(row=5,column=1,padx=15,pady=10)
        input_frame.pack(pady=10)
         
    def admin_menu():
        global title,input_frame, main_frame 
        title.destroy()
        if input_frame: input_frame.destroy()
        if main_frame: 
            main_frame.destroy()
            main_frame = None

        title=tk.Label(master=window,text='Admin Menu',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        enter_voter_details_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text=' Enter Voter Details ',command=enter_voter_details_menu, width=20)
        enter_voter_details_btn.grid(row=1,column=0,padx=15,pady=10)
        enter_candidate_details_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Enter Candidate Details',command=enter_candidate_details, width=20)
        enter_candidate_details_btn.grid(row=1,column=1,padx=15,pady=10)
        data_eraser_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text=' Data Eraser ',command=data_eraser, width=20)
        data_eraser_btn.grid(row=1,column=2,padx=15,pady=10)
        
        voted_or_not_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Voted and Not Voted List',command=voted_or_not, width=20)
        voted_or_not_btn.grid(row=2,column=0,padx=15,pady=10)
        start_voting_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text=' Start Voting ',command=start_voting, width=20)
        start_voting_btn.grid(row=2,column=1,padx=15,pady=10)
        stop_voting_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text=' Stop Voting ',command=stop_voting, width=20)
        stop_voting_btn.grid(row=2,column=2,padx=15,pady=10)
        
        view_current_poll_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='View Current Poll',command=view_current_poll, width=20)
        view_current_poll_btn.grid(row=3,column=1,padx=15,pady=10) 
        
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=go_to_main_menu, width=10)
        exit_btn.grid(row=5,column=0, columnspan=3, padx=15,pady=30) 
        
        input_frame.pack(pady=10)

    def go_to_admin_menu():
        global user_id,password,aadhar_number,admin_login_key
        
        try:
            input_id = int(user_id.get())
            input_aadhar = int(aadhar_number.get())
            input_password = int(password.get())
        except ValueError:
            pyautogui.alert('Invalid numeric entry in ID, Aadhar, or Password.')
            return
            
        if input_id == admin_login_key[0] and input_aadhar == admin_login_key[1] and input_password == admin_login_key[2]:
            admin_menu()
        else:
            pyautogui.alert('Wrong credentials: No records found. Please re-evaluate your entry.')
            
    def admin_login():
        global title,input_frame,user_id,password,aadhar_number
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Admin Login',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        user_id_title=tk.Label(master=input_frame,text='User Id:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        user_id_title.grid(row=1,column=0,padx=15,pady=10, sticky='w')
        user_id=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        user_id.grid(row=1,column=1,padx=15,pady=10, sticky='ew')
        
        aadhar_number_title=tk.Label(master=input_frame,text='Aadhar Number:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        aadhar_number_title.grid(row=2,column=0,padx=15,pady=10, sticky='w')
        aadhar_number=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        aadhar_number.grid(row=2,column=1,padx=15,pady=10, sticky='ew')
        
        password_title=tk.Label(master=input_frame,text='Password:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        password_title.grid(row=3,column=0,padx=15,pady=10, sticky='w')
        password=tk.Entry(master=input_frame,show='*',font='helvetica 18', width=20)
        password.grid(row=3,column=1,padx=15,pady=10, sticky='ew')
        
        show_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Show',command=lambda: password.config(show="" if password.cget("show")=="*" else "*"))
        show_btn.grid(row=3,column=2,padx=15,pady=10)
        
        def admin_check():
            if not user_id.get().isdigit() or not aadhar_number.get().isdigit():
                pyautogui.alert('Error: User ID and Aadhar must be numeric.')
                return
            if len(aadhar_number.get())!=12:
                pyautogui.alert('Error: Aadhar Number must be exactly 12 digits.')
                return
                
            go_to_admin_menu()
            
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=go_to_main_menu, width=10)
        exit_btn.grid(row=5,column=0,padx=15,pady=20)
        submit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Submit',command=admin_check, width=10)
        submit_btn.grid(row=5,column=1,padx=15,pady=20)
        
        input_frame.pack(pady=10)

    # --- VOTER/CANDIDATE VIEWING FUNCTIONS ---
    
    def next_():
        global title,input_frame,k,i, CANDIDATE_FILE
        
        if not k:
            try:
                with open(CANDIDATE_FILE,'r',newline='') as f:
                    m=csv.reader(f)
                    next(m, None) # Skip header row
                    for row in m:
                        if len(row) > 0:
                            k.extend(row)
            except FileNotFoundError:
                pyautogui.alert('Candidate data file not found! Please inform the administrator.')
                voter_menu()
                return

        # Check if we've reached the end of the list
        if i >= len(k):
             pyautogui.alert('Reached the end of the candidate list.')
             return
             
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Seeing Candidates',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        candidate_id_title=tk.Label(master=input_frame,text='Candidate Id:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_id_title.grid(row=1,column=0,padx=15,pady=10, sticky='w')
        candidate_name_title=tk.Label(master=input_frame,text='Candidate Name:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_name_title.grid(row=2,column=0,padx=15,pady=10, sticky='w')
        candidate_motto_title=tk.Label(master=input_frame,text='Candidate Motto:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        candidate_motto_title.grid(row=3,column=0,padx=15,pady=10, sticky='w')
        
        # Displaying data which is stored sequentially in k. Rows are 6 elements long (ID, Name, Age, Aadhar, Motto, Votes)
        try:
            candidate_id_answer_title=tk.Label(master=input_frame,text=k[i],font='Calibri 18 bold',bg=idle_bg_color,fg='white')
            candidate_id_answer_title.grid(row=1,column=1,padx=15,pady=10, sticky='w')
            candidate_name_answer_title=tk.Label(master=input_frame,text=k[i+1],font='Calibri 18 bold',bg=idle_bg_color,fg='white')
            candidate_name_answer_title.grid(row=2,column=1,padx=15,pady=10, sticky='w')
            candidate_motto_answer_title=tk.Label(master=input_frame,text=k[i+4],font='Calibri 18 bold',bg=idle_bg_color,fg='white')
            candidate_motto_answer_title.grid(row=3,column=1,padx=15,pady=10, sticky='w')
        except IndexError:
             pyautogui.alert('Error: Candidate data format is corrupted or index out of range.')
             i -= 6 # Roll back to safe position
             voter_menu()
             return

        def next_candidate_entry():
            global i
            i += 6
            next_()
            
        def prev_candidate_entry():
            global i
            if i <= 0:
                pyautogui.alert('Already at the start of the list.')
                return
            i -= 12 # Roll back two entries (12 elements)
            next_()
        
        next_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Next',command=next_candidate_entry)
        next_btn.grid(row=6,column=2,padx=15,pady=10)
        prev_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Previous',command=prev_candidate_entry)
        prev_btn.grid(row=6,column=0,padx=15,pady=10)
        
        def back_to_menu():
             title.destroy()
             input_frame.destroy()
             # Simple check to see if we came from candidate login or voter menu
             # Note: This is a bit fragile and a better state management method should be used in production code
             try:
                 if 'candidate_login' in str(sys._getframe(2).f_code.co_name):
                     candidate_login()
                 else:
                     voter_menu()
             except:
                 voter_menu()


        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=back_to_menu)
        exit_btn.grid(row=6,column=1,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        i+=6 

    def voter_seeing_candidates():
        global i, k
        i=0
        k.clear()
        next_() 
        
    def candidate_login():
        global title,input_frame
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Candidate Menu',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        see_all_cnd_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='See All Candidates',command=voter_seeing_candidates, width=20)
        see_all_cnd_btn.grid(row=1,column=0,padx=15,pady=10)
        
        exit_btn= tk.Button(master=input_frame,font=('Calibri',20,'bold'),text='Back',command=go_to_main_menu, width=10)
        exit_btn.grid(row=5,column=0,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        
    # --- VOTER FUNCTIONS ---
    
    def see_if_voting_is_going():
        global title,input_frame,voting_going
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Voting Status',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        k='Voting Is Going On' if voting_going else 'Voting Is Stopped'
        voting_status_title=tk.Label(master=input_frame,text=k,font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        voting_status_title.grid(row=1,column=1,padx=15,pady=10)
        
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=vote)
        exit_btn.grid(row=5,column=0,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        
    # --- FIX 3: Use the stored string variable for submission ---
    def submit_vote_for_candidate():
        """Handles vote submission, updates files, and navigates back."""
        global voter_choice_id, logged_in_voter_id, VOTER_FILE, title, input_frame, input_frame1
        
        # Robust Check for Voter ID
        try:
            candidate_id = voter_choice_id.get()
            # USE THE STORED STRING VARIABLE, NOT THE DESTROYED ENTRY WIDGET
            current_voter_id = logged_in_voter_id 
        except Exception as e:
            pyautogui.alert(f'Critical Error during submission: Cannot retrieve stored Voter ID. Please re-login. ({e})')
            try:
                title.destroy()
                if input_frame: input_frame.destroy()
                go_to_main_menu()
            except:
                pass
            return
        
        if not current_voter_id:
            pyautogui.alert('Voter ID was lost. Please re-login.')
            voter_menu()
            return

        if not candidate_id.isdigit():
            pyautogui.alert('Please enter a valid numeric Candidate ID.')
            return
            
        # 1. Check if voter has already voted
        try:
            with open(VOTER_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader, None) 
                for row in reader:
                    if len(row) >= 5 and row[0] == current_voter_id and row[4].lower() == 'true':
                        pyautogui.alert('You have already cast your vote!')
                        # Manual Cleanup if already voted
                        try:
                            title.destroy() 
                            if input_frame: input_frame.destroy()
                            if input_frame1: input_frame1.destroy()
                        except:
                            pass
                        voter_menu() 
                        return
        except Exception as e:
             pyautogui.alert(f'Error checking voter status or reading file: {e}. Aborting vote.')
             return
             
        # 2. Update vote count
        vote_successful = update_candidate_vote(candidate_id)
        
        if vote_successful:
            # 3. Mark voter as voted
            mark_voter_as_voted(current_voter_id)
            pyautogui.alert(f'Vote successfully cast for Candidate ID: {candidate_id}')
            
            # Safer Navigation Cleanup
            try:
                title.destroy() 
                if input_frame: input_frame.destroy()
                if input_frame1: input_frame1.destroy()
            except:
                pass 
            voter_menu() # Navigate back to the voter menu
            
        else:
            # If the vote failed (e.g., candidate not found), the update function already alerted
            pass 
            
    def vote_for_candidate():
        global voting_going, title,input_frame,voter_choice_id, input_frame1, CANDIDATE_FILE
        
        if voting_going==True:
            title.destroy()
            if input_frame: input_frame.destroy()
            
            title=tk.Label(master=window,text='🗳️ Cast Your Vote',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
            title.pack(pady=10)
            
            input_frame1=tk.Frame(master=window,bg=idle_bg_color)
            input_frame1.pack(pady=5,padx=20, fill='x')
            
            scrollbar = tk.Scrollbar(input_frame1,bg=idle_bg_color)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox = tk.Listbox(input_frame1, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, height=10, width=50, font=('helvetica', 14))
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            try:
                with open(CANDIDATE_FILE,'r',newline='') as f:
                    m=csv.reader(f)
                    next(m, None) # Skip header row
                    for row in m:
                        if len(row) >= 5:
                            display_text = f"ID: {row[0]}    Name: {row[1]}    Motto: {row[4][:30]}..."
                            listbox.insert(tk.END, display_text)
                            
            except FileNotFoundError:
                pyautogui.alert('Candidate file not found. Cannot display list.')
                vote()
                return

            scrollbar.config(command=listbox.yview)
            
            input_frame=tk.Frame(master=window,bg=idle_bg_color)
            
            vc_title=tk.Label(master=input_frame,text='Enter Candidate Id (from list above) to Vote:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
            vc_title.grid(row=1,column=0,padx=15,pady=10)
            
            voter_choice_id=tk.Entry(master=input_frame,font='helvetica 18', width=10)
            voter_choice_id.grid(row=1,column=1,padx=15,pady=10)
            
            def destroy_vote_view():
                title.destroy()
                if input_frame: input_frame.destroy()
                if input_frame1: input_frame1.destroy()
                vote()
            
            exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=destroy_vote_view, width=10)
            exit_btn.grid(row=5,column=0,padx=15,pady=10)
            submit_vc_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Submit Vote',command=submit_vote_for_candidate, width=10)
            submit_vc_btn.grid(row=5,column=1,padx=15,pady=10)
            
            input_frame.pack(pady=10)
        else:
            pyautogui.alert('Voting is not taking place, please come back later.')
            vote()
            
    def vote():
        global title,input_frame, input_frame1
        title.destroy()
        if input_frame: input_frame.destroy()
        if input_frame1: 
            input_frame1.destroy()
            input_frame1 = None
        
        title=tk.Label(master=window,text='Vote Menu',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        see_if_voting_is_going_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='See If Voting Is Going',command=see_if_voting_is_going, width=20)
        see_if_voting_is_going_btn.grid(row=1,column=0,padx=15,pady=10)
        vote_for_candidate_btn=tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Vote',command=vote_for_candidate, width=20)
        vote_for_candidate_btn.grid(row=1,column=1,padx=15,pady=10)
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=voter_menu, width=10)
        exit_btn.grid(row=5,column=0,columnspan=2,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        
    def voter_menu():
        global title,input_frame
        title.destroy()
        if input_frame: input_frame.destroy()
        title=tk.Label(master=window,text='Voter Menu',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        see_candidates_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='See Candidates',command=voter_seeing_candidates, width=15)
        see_candidates_btn.grid(row=1,column=0,padx=15,pady=10)
        vote_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Vote',command=vote, width=15)
        vote_btn.grid(row=1,column=1,padx=15,pady=10)
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=go_to_main_menu, width=10)
        exit_btn.grid(row=5,column=0,columnspan=2,padx=15,pady=10)
        
        input_frame.pack(pady=10)
        
    # --- FIX 2: Store strings upon successful login ---
    def go_to_voter_menu():
        global user_id, aadhar_number, VOTER_FILE, logged_in_voter_id, logged_in_aadhar_number
        
        # Get the input strings from the Entry widgets
        input_id = user_id.get()
        input_aadhar = aadhar_number.get()
            
        found = False
        try:
            with open(VOTER_FILE,'r',newline='') as f:
                m=csv.reader(f)
                next(m, None) # Skip header row
                for row in m:
                    if len(row) > 0:    
                        if input_id==row[0] and input_aadhar==row[3]:
                            # Store the successful login strings (data)
                            logged_in_voter_id = input_id
                            logged_in_aadhar_number = input_aadhar
                            voter_menu()
                            found = True
                            break 
        except FileNotFoundError:
            pyautogui.alert('Voter file not found. Contact administrator.')
            return

        if not found:
             pyautogui.alert('Login failed: Voter ID or Aadhar not recognized.')
            
    def voter_login():
        global title,input_frame,user_id,aadhar_number
        title.destroy()
        input_frame.destroy()
        title=tk.Label(master=window,text='Voter Login',font='Calibri 36 bold',bg=idle_bg_color,fg='white')
        title.pack(pady=10)
        
        input_frame=tk.Frame(master=window,bg=idle_bg_color)
        
        user_id_title=tk.Label(master=input_frame,text='User Id:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        user_id_title.grid(row=1,column=0,padx=15,pady=10, sticky='w')
        # Assign Entry objects to global variables for temporary input capture
        user_id=tk.Entry(master=input_frame,font='helvetica 18', width=20) 
        user_id.grid(row=1,column=1,padx=15,pady=10, sticky='ew')
        
        aadhar_number_title=tk.Label(master=input_frame,text='Aadhar Number:',font='Calibri 18 bold',bg=idle_bg_color,fg='white')
        aadhar_number_title.grid(row=2,column=0,padx=15,pady=10, sticky='w')
        aadhar_number=tk.Entry(master=input_frame,font='helvetica 18', width=20)
        aadhar_number.grid(row=2,column=1,padx=15,pady=10, sticky='ew')
        
        def voter_check():
            if not user_id.get().isdigit() or not aadhar_number.get().isdigit():
                 pyautogui.alert('Error: User ID and Aadhar must be numeric.')
                 return
            if len(aadhar_number.get())!=12:
                pyautogui.alert('Error: Aadhar Number must be exactly 12 digits.')
                return
                
            go_to_voter_menu()
            
        exit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Back',command=go_to_main_menu, width=10)
        exit_btn.grid(row=5,column=0,padx=15,pady=20)
        submit_btn= tk.Button(master=input_frame,font=('Calibri',18,'bold'),text='Submit',command=voter_check, width=10)
        submit_btn.grid(row=5,column=1,padx=15,pady=20)
        
        input_frame.pack(pady=10)

    # ----------------------------------------------------
    # Initial execution calls MUST be after function definitions
    # ----------------------------------------------------

    main_menu()
    window.mainloop()

if __name__ == '__main__':
    # 1. Create the base directory (VotingData folder)
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        pyautogui.alert(f"Permission Error: Could not create folder at {BASE_DIR}. Please run as administrator or choose a different location.")
        sys.exit(1)
    
    # 2. Check and create the CSV files with headers
    if not VOTER_FILE.exists():
        with open(VOTER_FILE, 'w', newline='') as f:
            csv.writer(f).writerow(['Voter_id','Voter_name','Voter_age','Voter_aadhar_number','voted'])
            
    if not CANDIDATE_FILE.exists():
        with open(CANDIDATE_FILE, 'w', newline='') as f:
            # Added 'votes' header
            csv.writer(f).writerow(['Candidate_id','Candidate_name','Candidate_age','Candidate_aadhar_number','Candidate_motto', 'votes'])
            
    app()
