#Conducts various operations on a .truck file and other related operations

import io
from decimal import *
getcontext().prec = 4
n = 0
truckfiles = []
class Output_choice:
    def __init__(self):
        print("Choose method for output:\n1. Console\n2. Output.txt file\nAny other output will result in console display")
        try:
            choice = int(input("Enter choice: "))
        except:
            choice = 1
        match(choice):
            case (2):
                print("Writing to Output.txt")
                self.write_file = True
            case _:
                print("Writing to console")
                self.write_file = False
        if self.write_file:
            self.file = open('Output.txt','w',encoding="utf-8")
        return

    def display(self,text=""):
        if self.write_file:
           self.file.write(text+"\n")
        else:
            print(text)
        return

    def close(self):
        if self.write_file:
            self.file.close()
        return
            
class Node:

#Class objects:
#self.node, self.index, self.al_index, self.x, self.y, self.z, self.weight, self.node_opt, self.edit_group, self.z_mirror, self.duplicates, self.node_opt_initial

    def __init__(self,n_index,node_line,node_type,al_num=""):
        self.node = True
        self.index = n_index
        self.edit_group = []
        #node_type = 1 -> nodes2
        if node_type == 1:
            
            self.al_index = al_num
            
        #node_type = 0 -> nodes
        else:
            self.al_index = ""
        try:
            self.x = Decimal(node_line[0])
            self.y = Decimal(node_line[1])
            self.z = Decimal(node_line[2])
        except:
            print("Error reading node ",n_index," ",self.al_index)
            self.node = False
        self.weight = Decimal(-1)
        self.z_mirror = []
        self.duplicates = []
        if len(node_line)>3:
            options = node_line[3].lstrip().split(" ")
            if len(options)>1:
                try:
                    self.weight = Decimal(options[1])
                except:
                    print("Error with recognizing weight for node ",n_index)
                    self.weight = Decimal(-1)

            self.node_opt = options[0] 
        else:            
            self.node_opt = ""
            self.weight = Decimal(-1)

        self.node_opt_initial = "unmodified"

    def display_node(self,renum=False):
        if renum:
            line = ""
        else:  
            if self.al_index == "":
                line = str(self.index)
            else:
                
                line = self.al_index
                #print(line)
        line += ","+str(self.x)+","+str(self.y)+","+str(self.z)
        if self.node_opt != "":
            line += ","+self.node_opt
            l_chk = self.node_opt.find('l')
            if l_chk>=0:
                line+=" "+str(self.weight)

        return line

    def display_metadata(self):
        ret_list = []
        ret_list.append("Node "+str(self.get_index()))
        if not self.nodes_or_nodes2():
            ret_list.append("Numerical Index: "+str(self.index))
        ret_list.append("Coordinates: "+str(self.x)+", "+str(self.y)+", "+str(self.z))
        if len(self.z_mirror)>0:
            ret_list.append("Z-Mirror Nodes (numerical index only): "+str(self.z_mirror))
        if len(self.duplicates)>0:
            ret_list.append("Duplicate Nodes (numerical index only): "+str(self.duplicates))
        if self.node_opt != "":
            ret_list.append("Node Options: "+self.node_opt)
        if self.weight>Decimal(-1):
            ret_list.append("Node Weight (specified in line): "+str(self.weight))
        
        return ret_list.copy()
    
    def get_index(self):
        if self.al_index == "":
            return self.index
        else:
            return self.al_index

    def nodes_or_nodes2(self):
        if self.al_index == "":
            # No alphabetic index
            return True
        else:
            # Alphabetic index exists
            return False

    def verify_index(self,ind_compare):
        if ind_compare==self.al_index:
            return True
        else:
            try:
                digit_ind = int(ind_compare)
                if digit_ind==self.index:
                    return True
                else:
                    return False
            except:
                return False

            
    def set_mirror(self,mirror_ind):
        self.z_mirror.append(mirror_ind)
        print("Node ",self.index," mirrors node ",mirror_ind)
        return

    def add_duplicate_ref(self,dup_ind):
        self.duplicates.append(dup_ind)
        print("Node ",self.index," has duplicate node ",dup_ind)
        return
    
    def get_mirror(self):
        return self.z_mirror.copy()

    def get_duplicates(self):
        return self.duplicates.copy()
    
    def edit_node(self,field,value,mirror=False):
        match(field):
            case('x'):
                self.x+=value
            case('y'):
                self.y+=value
            case('z'):
                if mirror:
                    if self.z<0:
                        self.z-=value
                    else:
                        self.z+=value
                else:
                    self.z+=value
            case('+opt'):
                if self.node_opt_initial == "unmodified":
                    self.node_opt_initial = self.node_opt
                for i in value:
                    add_check = True
                    for j in self.node_opt:
                        if i==j:
                            add_check = False
                            break
                    if add_check:
                        self.node_opt += i
                        if i=='l':
                            self.weight=Decimal(0)
                            print("Setting weight to ",str(self.weight))

            case('-opt'):
                if self.node_opt_initial == "unmodified":
                    self.node_opt_initial = self.node_opt
                for i in value:
                    sub_check = False
                    for j in range(len(self.node_opt)):
                        if i==self.node_opt[j]:
                            sub_check = True
                            break
                    if sub_check:
                        self.node_opt = self.node_opt[:j]+self.node_opt[j+1:]
                
            case('weight'):
                check = self.node_opt.find('l')
                if check>=0:
                    self.weight+=value
                    if self.weight<0:
                        self.weight*=-1
                
        return

    def undo_edit(self,field,value="NONE",mirror=False):
        match(field):
            case('x'):
                self.x-=value
            case('y'):
                self.y-=value
            case('z'):
                if mirror:
                    if self.z<0:
                        self.z+=value
                    else:
                        self.z-=value
                else:
                    self.z-=value
            case('opt'):
                ini_l_chk = self.node_opt_initial.find('l')
                mod_l_chk = self.node_opt.find('l')
                if mod_l_chk and not ini_l_chk:
                    self.weight = Decimal(-1)
                    print("Removed weight for node ",self.index)
                self.node_opt = self.node_opt_initial
                self.node_opt_initial = "unmodified"
            case('weight'):
                check = self.node_opt.find('l')
                if check>0:
                    self.weight-=value
                    if self.weight<0:
                        self.weight*=Decimal(-1)
            
        return

    

    def get_edit_grps(self):
        return self.edit_group.copy()

class Beam:

#Class Objects:
#self.index, self.nodeA_index, self.nodeB_index, self.truck_index, self.options, self.visible, self.active

    def __init__(self,b_index,t_index,nodeA,nodeB,opt=""):
        global truckfiles
        self.index = b_index
        self.truck_index = t_index
        self.nodeA = nodeA
        self.nodeB = nodeB
        self.active = True
        self.options = opt
        if self.options.find('i')>=0:
            self.visible = False
        else:
            self.visible = True
        

    def display_beam(self,nA_renum=-1,nB_renum=-1):
        if nA_renum>-1:
            nA = str(nA_renum)
        else:
            nA = str(truckfiles[self.truck_index].nodes[self.nodeA].get_index())
        if nB_renum>-1:
            nB = str(nB_renum)
        else:
            nB = str(truckfiles[self.truck_index].nodes[self.nodeB].get_index())
        ret_str = nA + ", "+nB
        if self.options != "":
            ret_str += ", "+self.options
        return ret_str

    def check_active(self):
        return self.active
    
        

class Edit_node_groups:
    def __init__(self,e_index,t_index,n_list = []):
        global truckfiles
        self.index = e_index
        self.desc = ""
        self.edit_nodes = n_list
        self.edits = []
        self.undo_edits = []
        self.truck_index = t_index
        self.z_mirror_mode = False
        self.z_mirror_nodes = []
        for i in self.edit_nodes:
            truckfiles[self.truck_index].nodes[i].edit_group.append(self.index)
        print("Created Node Edit group at position ",self.index)

    def view_nodelist(self):
        l_str = "["
        for i in range(len(self.edit_nodes)):
            l_str += str(truckfiles[self.truck_index].nodes[self.edit_nodes[i]].get_index())
            if i<len(self.edit_nodes)-1:
                l_str += ", "

        l_str+="]"
        return l_str

    def add_desc(self,info):
        self.desc = info
        return
    

    def toggle_z_mirror(self):
        def set_mirror_mode(status):
            self.z_mirror_mode = status
            if self.z_mirror_mode:
                print("Z-mirror mode enabled")
            else:
                print("Z-mirror mode disabled")
            return
        
        if self.z_mirror_mode is False:
            if len(self.z_mirror_nodes)==0:
                truck = truckfiles[self.truck_index]
                mir_check = []
                temp_mir_list = []
                non_mirror_nodes = []
                
                for i in self.edit_nodes:
                    if len(truck.nodes[i].z_mirror)==0:
                        non_mirror_nodes.append(i)
                    else:
                        i_mir = truck.nodes[i].z_mirror[0]
                        temp_mir_list.append(i_mir)
                        check_to_add = True
                        for j in self.edit_nodes:
                            if i_mir == j:
                                check_to_add = False
                        if check_to_add:
                            mir_check.append(i_mir)
                if len(non_mirror_nodes)>0:
                    print("Some nodes without mirrors found.\n",non_mirror_nodes,"\nEdits to these nodes won't be reflected along z-axis.")

                if len(mir_check)>0:
                    print("Some external z-mirror nodes found that are not included in edit group\n",mir_check)
                    option = input("Add outstanding mirror nodes to edit group?\ny: Yes\nAnything else: No\nOnly if all mirror nodes are included then Z-mirror mode will work\nEnter choice: ")
                    if option=="y":
                        for i in mir_check:
                            self.edit_nodes.append(i)
                        print("Added nodes to edit list")
                    else:
                        print("Returning to menu")
                        return
                print("Creating full list of mirror nodes")
                self.z_mirror_nodes = temp_mir_list.copy()
                print("Mirror nodes found: ",self.z_mirror_nodes)

            set_mirror_mode(True)
        else:
            set_mirror_mode(False)
        return

    def change_nodelist(self):
        truck = truckfiles[self.truck_index]
        choice = 0
        while choice != -1:
            print("WIP! Implementation soon...")
            print("Nodelist: ",self.edit_nodes)
            print("Menu:")
            print("1. Add nodes")
            if len(self.edit_nodes)>1:
                print("2. Delete nodes")
            print("-1. Exit")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case(1):
                    print("Implementation soon!")
                case(2) if len(self.edit_nodes)>1:
                    print("Implementation soon!")
                case(-1):
                    print("Exiting")
                case _:
                    print("Invalid choice")

        return
    def create_edit(self,field,value):
        match(field):
            case('x'):
                #DO SOMETHING!
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].edit_node(field,value)
            case('y'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].edit_node(field,value)
            case('z'):
                #print("WIP!!")
                if self.z_mirror_mode:
                    print("Mirror")
                    #Do something
                    for i in self.edit_nodes:
                        i_node = truckfiles[self.truck_index].nodes[i]
                        if len(i_node.get_mirror())>0:
                            truckfiles[self.truck_index].nodes[i].edit_node(field,value,True)
                        else:
                            truckfiles[self.truck_index].nodes[i].edit_node(field,value)
                else:
                    print("No mirror")
                    for i in self.edit_nodes:
                        truckfiles[self.truck_index].nodes[i].edit_node(field,value)

            case('+opt'):
                 #print("WIP")
                 for i in self.edit_nodes:
                     truckfiles[self.truck_index].nodes[i].edit_node(field,value)

            case('-opt'):
                 #print("WIP")
                 for i in self.edit_nodes:
                     truckfiles[self.truck_index].nodes[i].edit_node(field,value)
            case('weight'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].edit_node(field,value)
                    

        if field == '+opt' or field == '-opt':
            if field == '+opt':
                value = '+'+value
            else:
                value = '-'+value

            field = 'opt'
        
        
        if len(self.edits)==0:
            edit_line = [field,value]
            self.edits.append(edit_line)
        else:
            check = False
            for i in range(len(self.edits)):
                if self.edits[i][0]==field:
                    self.edits[i].append(value)
                    check = True
                    break
            if check is False:
                edit_line = [field,value]
                self.edits.append(edit_line)
        print("Added new edit")
        
        if len(self.undo_edits)>0:
            for i in range(len(self.undo_edits)):
                if self.undo_edits[i][0]==field:
                    del self.undo_edits[i]
                    print("Cleared undo history for ",field)
                    break
        
        return

    def new_edit(self):
        
        
        choice = 0
        print("Choose what to edit:")
        print("1. x values")
        print("2. y values")
        if self.z_mirror_mode:
            print("3. z values - will be mirrored")
        else:
            print("3. z values - no mirroring")
        print("4. Edit options")
        print("5. Weight values - only nodes with option l (WIP)")
        print("Any other input: exit menu")
        try:
            choice = int(input("Enter choice: "))
        except:
            choice = 0
        match(choice):
            case(1):
                print("Enter amount to add/subtract from the x-values of the nodes")
                print("Any float/decimal number will be added to the values. Use - to denote subtraction")
                try:
                    diff = Decimal(input("Enter amount: "))
                except:
                    print("Invalid input. Returning to menu")
                    return
                if diff==Decimal(0):
                    print("Value must be non-zero to have any effect!\nReturning")
                else:
                    #Do editing!
                    self.create_edit('x',diff)

            case(2):
                print("Enter amount to add/subtract from the y-values of the nodes")
                print("Any float/decimal number will be added to the values. Use - to denote subtraction")
                try:
                    diff = Decimal(input("Enter amount: "))
                except:
                    print("Invalid input. Returning to menu")
                    return
                if diff==Decimal(0):
                    print("Value must be non-zero to have any effect!\nReturning")
                else:
                    #Do editing!
                    self.create_edit('y',diff)

            case(3):
                print("Enter amount to add/subtract from the z-values of the nodes")
                if self.z_mirror_mode:
                    print("Any float/decimal number will be added to the absolute amount for values. Use - to denote subtraction")
                else:
                    print("Any float/decimal number will be added to the values. Use - to denote subtraction")

                try:
                    diff = Decimal(input("Enter amount: "))
                except:
                    print("Invalid input. Returning to menu")
                    return
                if diff==Decimal(0):
                    print("Value must be non-zero to have any effect!\nReturning")
                else:
                    #Do editing!
                    self.create_edit('z',diff)
            case(4):
                opt_list = ['n','m','f','x','y','c','h','e','b','p','L','l']
                
                option = 0
                print("Choose how to edit options for nodes:")
                print("1. Add to option list")
                print("2. Subtract from option list")
                print("Anything else: Exit")
                try:
                    option = int(input("Enter choice: "))
                except:
                    option = 0
                match(option):
                    case(1):
                        print("List of possible option values: ",opt_list)
                        print("To add a value to options, type those values without spaces")
                        print("E.g.: mb - if values aren't already in node's option list, they will be added")
                        raw_add_list = input("Enter values to add to node option lists: ")
                        add_list = ""
                        for i in raw_add_list:
                            if len(add_list)>0:
                                if add_list.find(i)>=0:
                                    continue
                                
                            verify = False
                            for j in opt_list:
                                if i==j:
                                    verify = True
                                    break
                            if verify:
                                add_list+=i
                        if len(add_list)==0:
                            print("Did not recognize any value!")
                        else:
                            print("Recognized list: ",add_list)
                            find_l = add_list.find('l')
                            if find_l>0:
                                print("Option l cannot be modified using this function. Ignoring it.")
                                add_list = add_list[:find_l]+add_list[find_l+1:]
                            self.create_edit('+opt',add_list)
                    case(2):
                        print("List of possible option values: ",opt_list)
                        print("To subtract a value from options, type those values without spaces")
                        print("E.g.: mb - if values are already in node's option list, they will be deleted")
                        raw_sub_list = input("Enter values to subtract from node option lists: ")
                        sub_list = ""
                        for i in raw_sub_list:
                            if len(sub_list)>0:
                                if sub_list.find(i)>=0:
                                    continue
                                
                            verify = False
                            for j in opt_list:
                                if i==j:
                                    verify = True
                                    break
                            if verify:
                                sub_list+=i
                        if len(sub_list)==0:
                            print("Did not recognize any value!")
                        else:
                            print("Recognized list: ",sub_list)
                            find_l = sub_list.find('l')
                            if find_l>0:
                                print("Option l cannot be modified using this function. Ignoring it.")
                                sub_list = sub_list[:find_l]+sub_list[find_l+1:]
                            self.create_edit('-opt',sub_list)
                    case _:
                        print("Exiting")
                        return
            case(5):
                #print("WIP")
                print("Checking nodes with weight option disabled")
                disabled_list = []
                for i in self.edit_nodes:
                    check = truckfiles[self.truck_index].nodes[i].node_opt.find('l')
                    if check == -1:
                        disabled_list.append(i)

                if len(disabled_list)>0:
                    print("Found nodes without weight option!")
                    print("Nodes without weight option: ",disabled_list)
                    print("Weight edits to such nodes won't have any effect")
                    #print("TODO: Make nodes have weight option")
                    print("Do you wish to enable these nodes with weight option?")
                    print("y: Yes\nAnything else: No")
                    option = input("Enter choice: ")
                    if option == 'y':
                        print("Creating edit to add l option to nodes without it")
                        self.create_edit('+opt','l')
                        
                else:
                    print("All nodes have weight option enabled")

                print("Enter amount to add/subtract from the weight values of the nodes")
                print("Any float/decimal number will be added to the values. Use - to denote subtraction")
                try:
                    diff = Decimal(input("Enter amount: "))
                except:
                    print("Invalid input. Returning to menu")
                    return
                if diff==Decimal(0):
                    print("Value must be non-zero to have any effect!\nReturning")
                else:
                    #Do editing!
                    self.create_edit('weight',diff)                
                
                    
            case _:
                print("Exiting")
                
        return

    def undo_edit(self,field):
        value = 0
        for i in self.edits:
            if i[0]==field:
                if field!='opt':
                    temp = i[len(i)-1:]
                    value = temp[0]
                else:
                    value = "NONE"
                break
        if value==0:
            return
        
        match(field):
            case('x'):
                #print("DO SOMETHING")
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].undo_edit(field,value)
            case('y'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].undo_edit(field,value)
            case('z'):
                if self.z_mirror_mode:
                    print("Mirror")
                    #Do something
                    for i in self.edit_nodes:
                        i_node = truckfiles[self.truck_index].nodes[i]
                        if len(i_node.get_mirror())>0:
                            truckfiles[self.truck_index].nodes[i].undo_edit(field,value,True)
                        else:
                            truckfiles[self.truck_index].nodes[i].undo_edit(field,value)
                else:
                    print("No mirror")
                    for i in self.edit_nodes:
                        truckfiles[self.truck_index].nodes[i].undo_edit(field,value)
            case('opt'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].undo_edit(field)

            case('weight'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].undo_edit(field,value)
            
        for i in range(len(self.edits)):
            if self.edits[i][0]==field:
                if field!='opt':
                    del self.edits[i][len(self.edits[i])-1:]
                    if len(self.edits[i])==1:
                        del self.edits[i]
                else:
                    del self.edits[i]
                break
        
        if field=='opt':
            return
        
        if len(self.undo_edits)==0:
            undo_line = [field,value]
            self.undo_edits.append(undo_line)
        else:
            check = False
            for i in range(len(self.undo_edits)):
                if self.undo_edits[i][0]==field:
                    self.undo_edits[i].append(value)
                    check = True
                    break
            if check is False:
                undo_line = [field,value]
                self.undo_edits.append(undo_line)
        print("Undid edit")

        return

    def redo_edit(self,field):
        value = 0
        for i in self.edits:
            if i[0]==field:
                temp = i[len(i)-1:]
                value = temp[0]
                break

        match(field):
            case('x'):
                #DO SOMETHING!
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].edit_node(field,value)

            case('y'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].edit_node(field,value)

            case('z'):
                if self.z_mirror_mode:
                    print("Mirror")
                    #Do something
                    for i in self.edit_nodes:
                        i_node = truckfiles[self.truck_index].nodes[i]
                        if len(i_node.get_mirror())>0:
                            truckfiles[self.truck_index].nodes[i].edit_node(field,value,True)
                        else:
                            truckfiles[self.truck_index].nodes[i].edit_node(field,value)
                else:
                    print("No mirror")
                    for i in self.edit_nodes:
                        truckfiles[self.truck_index].nodes[i].edit_node(field,value)
                        
            case('weight'):
                for i in self.edit_nodes:
                    truckfiles[self.truck_index].nodes[i].edit_node(field,value)

        for i in range(len(self.undo_edits)):
            if self.undo_edits[i][0]==field:
                del self.undo_edits[i][len(self.undo_edits[i])-1:]
                if len(self.undo_edits[i])==1:
                    del self.undo_edits[i]
                break

        if len(self.edits)==0:
            redo_line = [field,value]
            self.edits.append(redo_line)
        else:
            check = False
            for i in range(len(self.edits)):
                if self.edits[i][0]==field:
                    self.edits[i].append(value)
                    check = True
                    break
            if check is False:
                redo_line = [field,value]
                self.edits.append(redo_line)

        print("Redid edit")

                
        return

    def print_decimal_list(self, p_list=[]):
        if len(p_list)==0:
            return
        
        r_str = "["
        for i in range(len(p_list)):
            r_str += str(p_list[i])
            if i<len(p_list)-1:
                r_str+=", "
        r_str +="]"
        
        return r_str
    
    def show_undo_history(self):
        print("Undo History:\nShows latest undo for each field")
        if len(self.undo_edits)==0:
            print("No undo history to show")
        else:
            for i in range(len(self.undo_edits)):
                print(i,": ",self.undo_edits[i][0],end=" ")
                print(self.print_decimal_list(self.undo_edits[i][len(self.undo_edits[i])-1:]))
                #for j in self.undo_edits[i][len(self.undo_edits[i])-1:]:
                #    print(str(j),end=" ")
                #print("]")
                #self.undo_edits[i][len(self.undo_edits[i])-1:])
        return
            
    
    def undo_menu(self):
        choice = 0
        while choice != -1:
            self.show_undo_history()
            print("Undo Menu:")
            print("1. Undo a field")
            print("2. Redo a field")
            print("-1. Exit menu")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case(1):
                    self.view_history(True)
                    option = -1
                    print("Do you want to undo any field?")
                    print("Enter integer corresponding to above fields to undo that field")
                    print("NOTE: An undo for options resets all nodes to the original options including the l option!\nNodes with l option added will have weight values cleared with undo.")
                    print("Anything else: Return to undo menu")
                    try:
                        option = int(input("Enter choice: "))
                    except:
                        option = -1
                    for i in range(len(self.edits)):
                        if option == i:
                            
                            self.undo_edit(self.edits[i][0])
                            print("Undo completed")
                            break
                    print("Returning")
                case(2):
                    #print("DO!")
                    self.show_undo_history()
                    print("Do you want to redo any field?")
                    print("Enter integer corresponding to above fields to redo that field")
                    print("Anything else: Return to undo menu")
                    try:
                        option = int(input("Enter choice: "))
                    except:
                        option = -1
                    for i in range(len(self.undo_edits)):
                        if option == i:
                            #Do redo
                            self.redo_edit(self.undo_edits[i][0])
                            print("Redo completed")
                            break
                    print("Returning")

                case(-1):
                    print("Exiting")
                case _:
                    print("Invalid choice")

          
        return

    def view_history(self,show_quick = False):
        print("Edit History:\nFrom earliest edit to latest")
        for i in range(len(self.edits)):
            print(i,": ",self.edits[i][0],end=" ")
            print(self.print_decimal_list(self.edits[i][1:]))
            #for j in self.edits[i][1:]:
            #    print(str(j),end=" ")
            #print("]")
        if show_quick:
            if len(self.edits)==0:
                print("No edits to show!")
            return
        print("Visit undo menu?")
        print("y: Go to undo menu")
        print("Anything else: Return to menu")
        choice = input("Enter choice: ")
        if choice=='y':
            self.undo_menu()
        else:
            print("Exiting")
        return
    
    
    def show_node_val(self):
        truckfiles[self.truck_index].display_manager("NODES",False,False,False,self.edit_nodes)
        return

    def print_edit_grp(self,write_file = False):
        if len(self.edits)==0:
            return "No edits"
        
        comp_string = ";Edit Group "+str(self.index)+" | "
        if self.desc != "":
            comp_string+=self.desc+" | "

        comp_string += "Nodes: "+str(self.edit_nodes)+" | "
        
        if self.z_mirror_mode:
            comp_string+=" Z-mirror: ON | "
        else:
            comp_string+=" Z-mirror: OFF | "
            
        for i in self.edits:
            comp_string+=str(i[0])+": "
            comp_string+="["
            if write_file and i[0]!='opt':
                comp_string+=str(sum(i[1:]))
            else:
                for j in i[1:]:
                    comp_string+=str(j)+", "
                comp_string = comp_string[:-2]
            comp_string+="] | "       
        return comp_string

    def edit_nodes_menu(self):
        #global truckfiles
        choice = 0
        while choice != -1:
            print("Node list: ",self.view_nodelist())
            print("Edit Nodes Menu")
            print("Z-Mirror mode: ",self.z_mirror_mode)
            print("1. Edit node values collectively")
            if len(self.edits)==0:
                print("2. Change list of nodes in edit group (WIP)")
                print("3. Toggle Z-Mirror mode")
            else:
                print("4. View edit history & undo menu")
            print("5. Show current node values")
            print("-1. Exit")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case(1):
                    self.new_edit()
                case(2) if len(self.edits)==0:
                    self.change_nodelist()
                case(3) if len(self.edits)==0:
                    self.toggle_z_mirror()
                case(4) if len(self.edits)>0:
                    self.view_history()
                case(5):
                    self.show_node_val()
                case(-1):
                    print("Exiting")
                case _:
                    print("Invalid choice")
        return



class Truck:
    def __init__(self,fname,t_index):
        self.file = fname
        self.index = t_index
        self.nodes = []
        self.beams = []
        self.n = 0
        self.ready = False
        self.node_edit_groups = []

    class def_data_grp():
    
        def __init__(self,index,t_index):
            self.index = index
            self.truck_index = t_index
            self.grp_type = "NONE"
            self.active = True
            self.n_list = []
            
        def find_type(self):
            return self.grp_type

        def check_active(self):
            return self.active

        def menu(self):
            print("No type specified")
            return

        def disp_nodelist(self):
            if len(self.n_list)>0:
                l_str = "["
                for i in range(len(self.n_list)):
                    l_str += str(truckfiles[self.truck_index].nodes[self.n_list[i]].get_index())
                    if i<len(self.n_list)-1:
                        l_str += ", "

                l_str+="]"
                return l_str
            else:
                return
                

    class set_node_defaults(def_data_grp):

        def __init__(self,index,t_index,param,n_list):
            self.index = index
            self.truck_index = t_index
            self.grp_type = "SND"
            try:
                self.loadweight = Decimal(param[0])
                self.traction = Decimal(param[1])
                self.buoyancy = Decimal(param[2])
                self.surface = Decimal(param[3])
                self.active = True
            except:
                self.active = False
            if len(param>4):
                self.options = param[4]
            else:
                self.options = ""
            
            
            self.n_list = n_list

        def menu(self):
            
            choice = 0
            while choice != -1:
                print("Menu for set_node_defaults")
                print("Nodelist: ",self.disp_nodelist())
                print("1. View all info")
                print("2. Edit parameters")
                print("-1. Exit menu")
            return
            
    def search_for_beam(self,nodeA,nodeB):
        beam_index = -1
        for beam in self.beams:
            if (beam.nodeA==nodeA and beam.nodeB==nodeB) or (beam.nodeB==nodeA and beam.nodeA==nodeB):
                beam_index = beam.index
                break
        return beam_index
    
    def read_truck(self):
        f = open(self.file, mode='r')
        lines = f.readlines()
        readl = False
        nodes2 = False
        beams = False
        nodes_keywords = ["set_node_defaults"]
        beams_keywords = ["set_beam_defaults","detacher_group"]
        lnum = -1
        for l in lines:
            lnum += 1
            l = l.lstrip()
            end_at = l.find(";")
            l = l[:end_at]
            if l == "":
                continue
            if l[0].isalpha():
                nodes_check = l=="nodes"
                nodes2_check  = l=="nodes2"
                beams_check = l=="beams"
                if nodes2_check:
                    readl = True
                    nodes2 = True
                    beams = False
                    print("Reading nodes2")
                    continue
                elif nodes_check:
                    readl = True
                    nodes2 = False
                    beams = False
                    print("Reading nodes")
                    continue
                elif beams_check:
                    readl = True
                    nodes2 = False
                    beams = True
                    print("Reading beams")
                    continue

            #break_keywords = ['submesh']
            
            if l[0].isalpha() and readl:
                # TODO: check for and read keywords!
                if beams:
                    find_key = False
                    for i in beams_keywords:
                        if l.find(i)!= -1:
                            find_key = True
                            break
                    if find_key == True: 
                        continue
                    
                    #else:
                    #    readl = False
                    #    continue
                else:
                    #print("2")
                    find_key = False
                    for i in nodes_keywords:
                        if l.find(i)!= -1:
                            find_key = True
                            break
                    if find_key == True:
                        #print("Found")
                        continue
                    #else:
                    #    readl = False
                    #    continue

                if l.find(',')<0:
                    readl = False
                    continue
                
##                find_key = False
##                for i in break_keywords:
##                    if l.find(i)!=-1:
##                        find_key = True
##                        break
##                if find_key == True:
##                    readl = False
##                    continue
            if readl:
                l = l.split(",")
                if nodes2:
                    #print(l)
                    al_num = l[0]
                    #nodes2 -> 3rd parameter = 1
                    new_node = Node(self.n,l[1:],1,al_num)
                    if new_node.node:
                        self.nodes.append(new_node)
                        self.n+=1
                    else:
                        print("Skipping nodes2 line")
                    True
                elif beams:
                    try:
                        nodeA = l[0].strip()
                        nodeB = l[1].strip()
                    except:
                        continue
                    if len(l)>2:
                        opt = l[2]
                    else:
                        opt = ""
                    nodeA_id = self.get_numeric_node_index(nodeA)
                    nodeB_id = self.get_numeric_node_index(nodeB)
                    if nodeA_id<0 or nodeB_id<0:
                        print("Error in recognizing beams line ",lnum)
                    elif self.search_for_beam(nodeA_id,nodeB_id)>-1:
                        print("Redundant beam. Ignoring line ",lnum)
                    else:                        
                        new_beam = Beam(len(self.beams),self.index,nodeA_id,nodeB_id,opt)
                        self.beams.append(new_beam)
                        print("New beam at line ",lnum,": ",new_beam.display_beam())
                else:
                    try:
                        num = int(l[0])
                        if num==self.n:
                            #nodes -> 3rd parameter = 0
                            new_node = Node(num,l[1:],0)
                            if new_node.node == False:
                                del new_node
                                placeholder = Node(num,["0","0","0"],0)
                                self.nodes.append(placeholder)
                                print("Added placeholder for node ",self.n)
                            else:
                                self.nodes.append(new_node)
                            self.n += 1
                    except:
                        print("Error reading line")

        if len(self.nodes)>0:
            self.ready = True
            print("Node count: ",len(self.nodes))
            print("Beam count: ",len(self.beams))
            self.find_mirrors_duplicates()
            return True
        else:
            return False
    def find_mirrors_duplicates(self):
        print("Node mirrors and duplicates will be identified according to numerical index")
        for i in self.nodes:
            for j in self.nodes:
                if i.index == j.index:
                    continue
                x_chk = i.x == j.x
                y_chk = i.y == j.y
                z_mir_chk = (i.z+j.z == 0) and (i.z>0 or j.z>0)
                if x_chk and y_chk:
                    if z_mir_chk:
                        i.set_mirror(j.index)
                    elif i.z==j.z:
                        i.add_duplicate_ref(j.index)
                
        return
    
    def get_numeric_node_index(self,str_index):
        match_found = False
        for i in self.nodes:
            
            match_found = i.verify_index(str_index)

            if match_found:
                return i.index
            
        return -1

    
    def inputlist_to_nodelist(self,inputlist=[]):
        for i in range(len(inputlist)):
            inputlist[i] = inputlist[i].strip()
        nodelist = []
        for i in inputlist:
            range_chk = i.find("-")
            if range_chk>0:
                i = i.split("-")
                try:
                    first = i[0]
                    last = i[1]
                except:
                    continue

                
                
                #alpha_chk1 = first[0].isalpha()
                #alpha_chk2 = last[0].isalpha()
                #if alpha_chk1:

                first_ind = self.get_numeric_node_index(first)

                if first_ind<0:
                    try:
                        first_ind = int(first)
                    except:
                        continue
                
                #if alpha_chk2:
                last_ind = self.get_numeric_node_index(last)
                
                if last_ind<0:
                    try:
                        last_ind = int(last)
                    except:
                        continue
                if first_ind>=last_ind or first_ind<0 or last_ind<0 or first_ind>=self.n or last_ind>=self.n:
                    continue
                else:
                    #TODO: Add range to edit_grp (each node index one by one)
                    for j in range(first_ind,last_ind+1):
                        nodelist.append(j)
                    
            else:
                #alpha_chk = i[0].isalpha()
                #if alpha_chk:
                i_ind = self.get_numeric_node_index(i)
                if i_ind<0:
                    try:
                        i_ind = int(i)
                    except:
                        continue

                if i_ind<0 or i_ind>=self.n:
                    continue
                else:
                    nodelist.append(i_ind)
        min_nodelist = []
        for i in nodelist:
            if len(min_nodelist)==0:
                min_nodelist.append(i)
            else:
                chk_to_add = True
                for j in min_nodelist:
                    if j==i:
                        chk_to_add = False
                        break
                if chk_to_add:
                    min_nodelist.append(i)

        return min_nodelist

    def inputlist_to_beamlist(self,inputlist=[]):
        for i in range(len(inputlist)):
            inputlist[i] = inputlist[i].strip()
        beamlist = []
        for i in inputlist:
            range_chk = i.find("-")
            if range_chk>0:
                i = i.split("-")
                try:
                    first = int(i[0])
                    last = int(i[1])
                    
                except:
                    continue

                #print(first," ",last)
                
                

                if first>=last or first<0 or last<0 or first>=len(self.beams) or last>=len(self.beams):
                    continue
                else:
                    #Add range to edit_grp (each beam index one by one)
                    for j in range(first,last+1):
                        beamlist.append(j)
                    
            else:
                #alpha_chk = i[0].isalpha()
                #if alpha_chk:
                
                try:
                    i_ind = int(i)
                except:
                    continue

                if i_ind<0 or i_ind>=len(self.beams):
                    continue
                else:
                    beamlist.append(i_ind)
        #print(beamlist)            
        min_beamlist = []
        for i in beamlist:
            if len(min_beamlist)==0:
                min_beamlist.append(i)
            else:
                chk_to_add = True
                for j in min_beamlist:
                    if j==i:
                        chk_to_add = False
                        break
                if chk_to_add:
                    min_beamlist.append(i)

        return min_beamlist


    def show_nodes(self,nodelist=[]):
        op = Output_choice()
        disp_nodes = False
        disp_nodes2 = False
        if len(nodelist)>0:
            print("Do you wish to renumber the nodes? (only for nodes and not nodes2)\ny: Renumber nodes\nAnything else: Keep numbering")
            renum_opt = input("Enter choice: ")
        edit_grps = []

        if len(nodelist)>0:
            for i in nodelist:
                i_list = self.nodes[i].edit_group.copy()
                if len(i_list)>0:
                    if len(edit_grps)==0:
                        edit_grps+=i_list
                    else:
                        for j in i_list:
                            add_grp = True
                            for k in edit_grps:
                                if j==k:
                                    add_grp = False
                                    break
                            if add_grp:
                                edit_grps+=j
        else:
            for i in self.nodes:
                i_list = i.edit_group.copy()
                if len(i_list)>0:
                    if len(edit_grps)==0:
                        edit_grps+=i_list
                    else:
                        for j in i_list:
                            add_grp = True
                            for k in edit_grps:
                                if j==k:
                                    add_grp = False
                                    break
                            if add_grp:
                                edit_grps+=j


        if len(edit_grps)>0:
#            print(edit_grps)
#            print(self.node_edit_groups)
            for i in edit_grps:
                k = self.node_edit_groups[i].print_edit_grp(True)
                if k != "No edits":
                    op.display(k)
        

        if len(nodelist)>0:
            num = 0
            for j in nodelist:
                node_type = self.nodes[j].nodes_or_nodes2()
                if node_type and disp_nodes != True:
                    op.display("nodes")
                    disp_nodes = True
                    disp_nodes2 = False
                elif node_type == False and disp_nodes2 != True:
                    op.display("nodes2")
                    disp_nodes2 = True
                    disp_nodes = False

                if renum_opt=="y" and disp_nodes:
                    op.display(str(num)+self.nodes[j].display_node(True))
                else:
                    op.display(self.nodes[j].display_node())
                num+=1
            if renum_opt:
                op.display(";Renumbered nodes: "+str(nodelist))
        else:
            for i in self.nodes:
                node_type = i.nodes_or_nodes2()
                if node_type and disp_nodes != True:
                    op.display("nodes")
                    disp_nodes = True
                    disp_nodes2 = False
                elif node_type == False and disp_nodes2 != True:
                    op.display("nodes2")
                    disp_nodes2 = True
                    disp_nodes = False
                op.display(i.display_node())
        op.close()
        del op
        return
    


    def view_truck(self):
            
        #menu code
        option = 0
        print("Choose what to display:")
        print("1. nodes & nodes2")
        print("2. beams")
        print("Anything else: all data")
        try:
            option = int(input("Enter choice: "))
        except:
            option = 0
        
        print("Choose selection of nodes to display data of?\ny: Yes\nAnything else: No")
        sel_opt = input("Enter choice: ")
        if sel_opt == "y":
            rec_n_list = input("List nodes to view collectively:\nUse - to denote ranges and , to distinguish between nodes and ranges\nE.g. 0,9-23,44\nEnter line: ").strip().split(",")
            min_rec_n_list = self.inputlist_to_nodelist(rec_n_list)
            if len(min_rec_n_list)==0:
                print("Error in reading input line for display")
                return
            
        match(option):
            case 1:
                if sel_opt=="y":
                    self.show_nodes(min_rec_n_list)
                else:
                    self.show_nodes()
            case _:
                if sel_opt=="y":
                    self.show_nodes(min_rec_n_list)
                else:
                    self.show_nodes()
       
        return

    def view_truck_new(self):
        choice = 0
        while choice != -1:
            print("Choose method to display: ")
            print("1. Using selection of nodes or a single node")
            print("2. Using selection of beams or a single beam")
            print("-1. Exit")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case (1):
                    self.view_by_nodes()
                case (2):
                    self.view_by_beams()
                case (-1):
                    print("Exiting")
                case _:
                    print("Invalid choice")

        return

    def view_by_nodes(self):
        choice = 0
        print("Enter which nodes to display:")
        print("1. All nodes")
        print("2. User defined selection of nodes")
        edit_grps_chk = len(self.node_edit_groups)>0
        if edit_grps_chk:
            print("3. Nodelist from Node Edit Group")
        print("Anything else: Exit")
        try:
            choice = int(input("Enter choice: "))
        except:
            choice = 0
        nodelist = []
        all_nodes = False
        match(choice):
            case(1):
                all_nodes = True
            case(2):
                print("Total number of nodes: ",self.n)
                print("Last node index: ",self.n-1)
                nodelist_str = input("List nodes to view collectively:\nUse - to denote ranges and , to distinguish between nodes and ranges\nE.g. 0,9-23,44\nEnter line: ")
                if len(nodelist_str)==0:
                    print("No input! Returning")
                    return
                else:
                    nodelist_ = nodelist_str.strip().split(",")
                print(nodelist_)
                
                    
                nodelist = self.inputlist_to_nodelist(nodelist_)
                
                print(nodelist)
                if len(nodelist)==0:
                    print("Error in reading input line")
                    return
            case(3) if edit_grps_chk:
                #Get from edit groups
                print("List of node edit groups and positions:")
                for i in range(len(self.node_edit_groups)):
                    print(i," ",self.node_edit_groups[i].view_nodelist())
                pos = 0
                try:
                    pos = int(input("Enter position of node edit group to use nodelist from: "))
                except:
                    pos = -1
                if pos<0 or pos>=len(self.node_edit_groups):
                    print("Out of bounds")
                    return
                else:
                    nodelist = self.node_edit_groups[pos].edit_nodes.copy()
            case _:
                print("Exiting")
                return

        opt_show_beams = False
        opt_renum = False
        
        choice = 0
        while choice !=-1 and len(nodelist)>1:
            print("View Options Menu - select an option to toggle it:")
            print("1. Show beams - ",opt_show_beams)
            if not all_nodes:
                print("2. Renumber nodes - ",opt_renum)
            print("Anything else: Continue to display")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case (1):
                    opt_show_beams = not opt_show_beams
                case (2) if not all_nodes:
                    opt_renum = not opt_renum
                case _:
                    choice = -1
                    print("Continuing to display")

        if len(nodelist)==1:
            print("Showing metadata of node ",self.nodes[nodelist[0]].get_index())

        #"NODES",all_nodes,opt_show_beams,opt_renum,nodelist
        if all_nodes:
            self.display_manager("NODES",all_nodes,opt_show_beams,False)
        else:
            self.display_manager("NODES",all_nodes,opt_show_beams,opt_renum,nodelist)
        return

    def view_by_beams(self):
        choice = 0
        print("Enter which beams to display:")
        print("1. All beams")
        print("2. User defined selection of beams")
        print("Anything else: Exit")
        try:
            choice = int(input("Enter choice: "))
        except:
            choice = 0
        all_beams = False
        beamlist = []
        match(choice):
            case 1:
                all_beams = True
            case 2:
                print("You will need to specify the beams to display using their numerical indices")
                print("Show beams with numerical indices?")
                print("y: Yes")
                print("Anything else: No")
                option = input("Enter choice: ")
                if option == 'y':
                    b_list = self.display_beams(False,["INDICES"])
                    for i in b_list:
                        print(i)

                beamlist_str = input("List beams (by indices) to view collectively:\nUse - to denote ranges and , to distinguish between single beams and ranges\nE.g. 0,9-23,44\nEnter line: ")
                if len(beamlist_str)==0:
                    print("No input! Returning")
                    return
                else:
                    beamlist_ = beamlist_str.strip().split(",")
                print(beamlist_)
                
                    
                beamlist = self.inputlist_to_beamlist(beamlist_)
                
                print(beamlist)
                if len(beamlist)==0:
                    print("Error in reading input line")
                    return

                
            case _:
                print("Exiting")
                return
        opt_show_nodes = False
        opt_renum = False
        
        choice = 0
        while choice !=-1:
            print("View Options Menu - select an option to toggle it:")
            print("1. Show nodes - ",opt_show_nodes)
            if not all_beams:
                print("2. Renumber nodes - ",opt_renum)
            print("Anything else: Continue to display")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case (1):
                    opt_show_nodes = not opt_show_nodes
                case (2) if not all_beams:
                    opt_renum = not opt_renum
                case _:
                    choice = -1
                    print("Continuing to display")

        #"BEAMS",all_beams,opt_show_nodes,opt_renum,beamlist
        if all_beams:
            self.display_manager("BEAMS",all_beams,opt_show_nodes,False)
        else:
            self.display_manager("BEAMS",all_beams,opt_show_nodes,opt_renum,beamlist)
        return

    def find_nodes_from_beams(self,beamlist):
        nodelist = []
        for i in beamlist:
            if len(nodelist)==0:
                nodelist.append(self.beams[i].nodeA)
                nodelist.append(self.beams[i].nodeB)
            else:
                chk_nodeA = False
                chk_nodeB = False
                for j in nodelist:
                    if j==self.beams[i].nodeA:
                        chk_nodeA = True
                    elif j==self.beams[i].nodeB:
                        chk_nodeB = True
                if not chk_nodeA:
                    nodelist.append(self.beams[i].nodeA)

                if not chk_nodeB:
                    nodelist.append(self.beams[i].nodeB)
                        
        return nodelist.copy()

    def find_beams_from_nodes(self,nodelist):
        beamlist = []
        for i in range(len(self.beams)):
            nodeA = self.beams[i].nodeA
            nodeB = self.beams[i].nodeB
            chk_nodeA = False
            chk_nodeB = False
            for j in nodelist:
                if j==nodeA:
                    chk_nodeA = True
                elif j==nodeB:
                    chk_nodeB = True
            if chk_nodeA and chk_nodeB:
                beamlist.append(i)
            
        return beamlist.copy()
    
    def display_manager(self,data_type,all_data,opt_show_cmplmnt_data,opt_renum,datalist=[]):
        #MAKE FUNCTION TO SHOW NODE METADATA
        #Show nodes
        nodelist = []
        n_list = []
        if data_type == "NODES":
            if all_data:
                n_list = self.display_nodes(False)
            elif len(datalist)==1:
                n_list = self.nodes[datalist[0]].display_metadata()
            else:
                n_list = self.display_nodes(opt_renum,datalist)
        elif opt_show_cmplmnt_data:
            if all_data:
                n_list = self.display_nodes(False)
            #FIND NODES MENTIONED IN BEAMS!!
            else:
                nodelist = self.find_nodes_from_beams(datalist)
                n_list = self.display_nodes(opt_renum,nodelist)
                

        #Show beams
        beamlist = []
        b_list = []
        if data_type == "BEAMS":
            if all_data:
                b_list = self.display_beams(False,[])
            elif len(nodelist)>0:
                b_list = self.display_beams(opt_renum,datalist,nodelist)
            else:
                b_list = self.display_beams(opt_renum,datalist)
        elif opt_show_cmplmnt_data:
            if all_data:
                b_list = self.display_beams(False,[])
            #FIND BEAMS MENTIONED IN NODE LIST!
            else:
                beamlist = self.find_beams_from_nodes(datalist)
                b_list = self.display_beams(opt_renum,beamlist,datalist)

        op = Output_choice()
        #Print all stuff
        if len(n_list)>0:
            for i in n_list:
                op.display(i)
        if len(b_list)>0:
            for i in b_list:
                op.display(i)
        op.close()
        return

    def display_nodes(self,opt_renum,nodelist=[]):
        ret_list = []
        disp_nodes = False
        disp_nodes2 = False
        edit_grps = []

        if len(nodelist)>0:
            for i in nodelist:
                i_list = self.nodes[i].edit_group.copy()
                if len(i_list)>0:
                    if len(edit_grps)==0:
                        edit_grps+=i_list
                    else:
                        for j in i_list:
                            add_grp = True
                            for k in edit_grps:
                                if j==k:
                                    add_grp = False
                                    break
                            if add_grp:
                                edit_grps+=j
        else:
            for i in self.nodes:
                i_list = i.edit_group.copy()
                if len(i_list)>0:
                    if len(edit_grps)==0:
                        edit_grps+=i_list
                    else:
                        for j in i_list:
                            add_grp = True
                            for k in edit_grps:
                                if j==k:
                                    add_grp = False
                                    break
                            if add_grp:
                                edit_grps+=j


        if len(edit_grps)>0:
#            print(edit_grps)
#            print(self.node_edit_groups)
            for i in edit_grps:
                k = self.node_edit_groups[i].print_edit_grp(True)
                if k != "No edits":
                    #op.display(k)
                    ret_list.append(k)
        

        if len(nodelist)>0:
            num = 0
            for j in nodelist:
                node_type = self.nodes[j].nodes_or_nodes2()
                if node_type and disp_nodes != True:
                    #op.display("nodes")
                    ret_list.append("nodes")
                    disp_nodes = True
                    disp_nodes2 = False
                elif node_type == False and disp_nodes2 != True:
                    #op.display("nodes2")
                    ret_list.append("nodes2")
                    disp_nodes2 = True
                    disp_nodes = False

                if opt_renum and disp_nodes:
                    #op.display(str(num)+self.nodes[j].display_node(True))
                    ret_list.append(str(num)+self.nodes[j].display_node(True))
                else:
                    #op.display(self.nodes[j].display_node())
                    ret_list.append(self.nodes[j].display_node())
                num+=1
            if opt_renum:
                #op.display(";Renumbered nodes: "+str(nodelist))
                ret_list.append(";Renumbered nodes: "+str(nodelist)) #MAKE FUNCTION TO DISPLAY NODELIST!
        else:
            for i in self.nodes:
                node_type = i.nodes_or_nodes2()
                if node_type and disp_nodes != True:
                    #op.display("nodes")
                    ret_list.append("nodes")
                    disp_nodes = True
                    disp_nodes2 = False
                elif node_type == False and disp_nodes2 != True:
                    #op.display("nodes2")
                    ret_list.append("nodes2")
                    disp_nodes2 = True
                    disp_nodes = False
                #op.display(i.display_node())
                ret_list.append(i.display_node())
        
        return ret_list.copy()

    def display_beams(self,opt_renum,beamlist,renum_nodes=[]):
        ret_list = []
        #print(renum_nodes)
        if opt_renum:
            #renum_nodes must have nodes here
            if len(beamlist)>0:
                ret_list.append("beams")
                for i in beamlist:
                    nA = self.beams[i].nodeA
                    nB = self.beams[i].nodeB
                    
                    if self.nodes[nA].nodes_or_nodes2():
                        
                        for j in range(len(renum_nodes)):
                            #print(j," - ",renum_nodes[j], " match with ",nA)
                            if nA==renum_nodes[j]:
                                node_A = j
                                break
                    else:
                        node_A = -1

                    if self.nodes[nB].nodes_or_nodes2():
                        
                        for j in range(len(renum_nodes)):
                            #print(j," - ",renum_nodes[j], " match with ",nB)
                            if nB==renum_nodes[j]:
                                node_B = j
                                break
                    else:
                        node_B = -1

                    print(node_A," ",node_B)
                    k = self.beams[i].display_beam(node_A,node_B)
                    print(k)
                    ret_list.append(k)

        else:
            ret_list.append("beams")
            if len(beamlist)>0:
                #print(beamlist)
                #Make option to use indices!
                if beamlist[0]=="INDICES":
                    for i in range(len(self.beams)):
                        ret_list.append(str(i)+": "+self.beams[i].display_beam())
                else:
                    for i in beamlist:
                        print("Beam ",i,": ",self.beams[i].display_beam())
                        ret_list.append(self.beams[i].display_beam())
            else:
                for i in self.beams:
                    ret_list.append(i.display_beam())
                      
                    
        return ret_list.copy()
    
    def create_new_edit_grp(self):
        print("Total number of nodes: ",self.n)
        print("Last node index: ",self.n-1)
        edit_grp_str = input("List nodes to edit collectively:\nUse - to denote ranges and , to distinguish between nodes and ranges\nE.g. 0,9-23,44\nEnter line: ")
        if len(edit_grp_str)==0:
            print("No input! Returning")
            return
        else:
            edit_grp_lst = edit_grp_str.strip().split(",")
        print(edit_grp_lst)
        
            
        min_edit_grp = self.inputlist_to_nodelist(edit_grp_lst)
        
        print(min_edit_grp)
        if len(min_edit_grp)==0:
            print("Error in reading input line")
            return
        new_edit_grp = Edit_node_groups(len(self.node_edit_groups),self.index,min_edit_grp.copy())
        self.node_edit_groups.append(new_edit_grp)
        return

    def edit_grp_menu(self):
        choice = 0
        while choice != -1:
            if len(self.node_edit_groups)==0:
                self.create_new_edit_grp()
                if len(self.node_edit_groups)==0:
                    print("Returning to menu")
                    return
            else:
                print("Edit Group Menu:")
                print("1. Create a new node edit group")
                print("2. Select a node edit group to edit")
                print("-1. Exit")
                try:
                    choice = int(input("Enter choice: "))
                except:
                    choice = 0
                match(choice):
                    case(1):
                        self.create_new_edit_grp()
                    case(2):
                        print("List of node edit groups and positions:")
                        for i in range(len(self.node_edit_groups)):
                            print(i," ",self.node_edit_groups[i].view_nodelist())
                        pos = 0
                        try:
                            pos = int(input("Enter position of node edit group to modify: "))
                        except:
                            pos = -1
                        if pos<0 or pos>=len(self.node_edit_groups):
                            print("Out of bounds")
                        else:
                            self.node_edit_groups[pos].edit_nodes_menu()
                    case(-1):
                        print("Exiting")
                    case _:
                        print("Invalid choice")
        return

    def create_flares(self):
        print("Creates headlight flares for a vehicle based on 1 lead node\nNode must have a non-zero z value!")
        ld_node_ind = input("Enter index of lead node to use: ")
        ld_node = None
        check = False
        for i in self.nodes:
            if i.verify_index(ld_node_ind):
                ld_node = i
                check = True
                break
        if check is False:
            print("Node not found")
            return
        elif ld_node.z==0:
            print("Node in center  of z-axis! Won't be able to create flares with this node!")
            return
        print("Creating headlight flares")
        try:
            mir_ld_node = self.nodes[ld_node.get_mirror()[0]]
        except:
            print("Mirror to lead node not found; returning to menu")
            return
        n_candidates = []
        x_chk_best = False
        for i in self.nodes:
            
            y_chk = ld_node.y<i.y
            x_chk = (ld_node.x>=i.x) or (ld_node.x+Decimal(0.1)>=i.x)
            z_chk = (ld_node.z>0 and i.z>0) or (ld_node.z<0 and i.z<0)
            x_chk_better = ld_node.x<=i.x+Decimal(0.1)
            x_chk_best_i = ld_node.x==i.x
            z_chk_better = abs(ld_node.z-i.z)<=Decimal(0.1)
            mir_chk = len(i.get_mirror())>0
            rating = 0
            
            if mir_chk:
                if x_chk and y_chk and z_chk:
                    if x_chk_best_i:
                        rating+=2
                        x_chk_best = True
                    elif x_chk_better:
                        rating+=1

                    if z_chk_better:
                        rating+=1

                    n_candidates.append((i.index,rating))

        print(n_candidates)
        if len(n_candidates)==0:
            print("Unable to find good reference nodes for this lead node.\nTry using a .truck file with more mirror nodes or a different lead node")
            return
        ref_node_ind = -1
        best_rating = 0
        for i in n_candidates:
            if i[1]>best_rating or ref_node_ind==-1:
                ref_node_ind = i[0]
                best_rating = i[1]
        if best_rating==0:
            closest = -1
            for i in n_candidates:
                if closest==-1:
                    closest = i[0]
                else:
                    closest_node = self.nodes[closest]
                    i_node = self.nodes[i[0]]
                    clos_dif = abs(closest_node.x-ld_node.x)
                    i_dif = abs(i_node.x-ld_node.x)
                    if i_dif<clos_dif:
                        closest = i[0]
            ref_node_ind = closest
        print("Selected reference node: ",ref_node_ind)
        ref_node = self.nodes[ref_node_ind]
        try:
            mir_ref_node = self.nodes[ref_node.get_mirror()[0]]
        except:
            print("Internal error!! Returning")
            return
        if x_chk_best is False:
            disp_x_recom = False
            print("Flares won't be perfectly aligned to light up front path.\nWould you like to edit nodes to adjust the change?")
            print("y: Yes\nAnything else: No")
            option = input("Enter choice: ")
            if option=='y':
                new_edit_grp = Edit_node_groups(len(self.node_edit_groups),self.index,[ref_node.index,mir_ref_node.index])
                new_edit_grp.add_desc("Flare creation adjustments")
                diff = ld_node.x-ref_node.x
                print("Difference: ",diff)
                new_edit_grp.create_edit('x',diff)
                self.node_edit_groups.append(new_edit_grp)
                print("Show current node values?\ny: Yes\nAnything else: No")
                option = input("Enter choice: ")
                if option == 'y':
                    new_edit_grp.show_node_val()
                
                print("Relevant nodes adjusted")
            else:
                disp_x_recom = True
        
        #Flare line creation
        f_line1 = ""
        f_line2 = ""
        if ld_node.z > 0:
            f_line1 += str(ld_node.index)+","+str(ref_node.index)+","+str(mir_ld_node.index)+","
            f_line2 += str(mir_ld_node.index)+","+str(ld_node.index)+","+str(mir_ref_node.index)+"," 
        else:
            f_line1 += str(ld_node.index)+","+str(mir_ld_node.index)+","+str(ref_node.index)+","
            f_line2 += str(mir_ld_node.index)+","+str(mir_ref_node.index)+","+str(ld_node.index)+","
        #print(f_line1)
        #print(f_line2)
        f_line_mid =  " 0, 0, 0, f, -1, 0,"
        f_line1 += f_line_mid
        f_line2 += f_line_mid
        option = input("Enter flare size to set or any value less or equal to 0.001 for invisible flare: ")
        try:
            flare_size = Decimal(option)
            if flare_size<0.001:
                print("Changing size to 0.001")
                flare_size = 0.001
            f_line1 += " "+str(flare_size)+" default"
            f_line2 += " "+str(flare_size)+" default"
        except:
            f_line1 += " 0.001 default"
            f_line2 += " 0.001 default"
        
        
        op = Output_choice()
        op.display("flares2\n;headlights (auto-generated)")
        op.display(f_line1)
        op.display(f_line2)
        if x_chk_best is False and disp_x_recom:
            op.display("Recommended x value for nodes "+str(ref_node.index)+" & "+str(mir_ref_node.index)+": "+str(ld_node.x))
        op.close()
        return

    def trucknodes2tobj(self):
        odef = []
        odefv = []
        try:
            k = int(input("Enter number of objects to use for coordinates: "))
        except:
            k = 1
            print("Problem with input. Using 1 object instead.")
        if k<1:
            k = 1
            print("Lower than 1. Resetting to 1 object.")
        elif k>1:
            print("NOTE: objects will be listed one after another in output lines.")
        print("Enter object name(s) with their rotations separated by commas:\nE.g.: house, 90, 0, 90")
        for i in range(k):
            odefv.clear()
            print("Object ", end="")
            odefv = input(f'{i}: ').split(',')
            try:
                val = 1
                while val <= 3:
                    check = Decimal(odefv[val])
                    odefv[val] = Decimal(odefv[val])
                    val += 1
            except:
                print("Problem with rotations!")
                return
            odef.append(odefv.copy())
        offset = input("Enter coordinates to offset nodes into map positions:\nE.g.: 512, 0, 512\n").split(',')
        try:
            count = 0
            for i in offset:
                offset[count] = Decimal(i)
                count+=1
        except:
            offset = [0,0,0]
            print("Problem with offset input; resetting it to 0")
        dup_n_list = []
        for i in self.nodes:
            i_d_list = i.get_duplicates()
            if len(dup_n_list)==0:
                dup_n_list += i_d_list
            else:
                for j in i_d_list:
                    check_match = False
                    for n_l in dup_n_list:
                        if j==n_l:
                            check_match = True
                            break
                    if check_match is False:
                        dup_n_list.append(j)
                        
        print("Duplicate nodes: ",dup_n_list)
        print("Ignoring these entries")
        op = Output_choice()
        count = 0
        for i in self.nodes:
            #print(count)
            check_dup = False
            for j in dup_n_list:
                if i.index == j:
                    check_dup = True
                    break
            if check_dup:
                continue
                
            x = i.x+offset[0]
            y = i.y+offset[1]
            z = i.z+offset[2]
            cur_obj = odef[count%k]
            op.display(f'{x}, {y}, {z}, {cur_obj[1]}, {cur_obj[2]}, {cur_obj[3]}, {cur_obj[0]}')
            count+=1
        op.close()
        del op
        return


    
    def menu(self):
        choice = 0
        while choice != -1:
            print("Menu for ",self.file,":")
            print("1. View data groups")
            print("2. Edit nodes menu")
            print("--Truck file section creation--")
            print("51. Auto-create headlight flares")
            print("--Truck file conversion operations--")
            print("101. Convert nodes to map coordinates - .tobj format")
            print("-1. Exit")
            try:
                choice = int(input("Enter choice: "))
            except:
                choice = 0
            match(choice):
                case(1):
                    self.view_truck_new()
                case(2):
                    self.edit_grp_menu()

                case(51):
                    self.create_flares()

                case(101):
                    self.trucknodes2tobj()
                
                case(-1):
                    print("Exiting menu")
                case _:
                    print("Invalid choice")

        return
            

def new_torquecurve():
    t_curve = []
    print("Enter lines for torquecurve in such a manner:\nrpm,current_torque\nEnter STOP to stop lines")
    stop = False
    while stop == False:
        try:
            check = input()
            if check == "STOP":
                break
            t_line_raw = check.split(',')
            t_line = []
            t_line.append(int(t_line_raw[0]))
            t_line.append(int(t_line_raw[1]))
            t_curve.append(t_line.copy())
            t_line.clear()
        except:
            print("Error reading line!")
    max_torque = 0
    for i in t_curve:
        if i[1] > max_torque:
            max_torque = i[1]
    for i in t_curve:
        i.append(i[1]/max_torque)

    op = Output_choice()
    op.display("Max torque: "+str(max_torque))
    op.display("torquecurve")
    for i in t_curve:
        op.display(str(i[0])+","+str(i[2]))
    op.close()
    del op
    
    return

def menu():
    global n, truckfiles
    option = 0
    while option != -1:
        print("Main Menu:")
        print("1. Open a .truck file")
        if n>0:
            print("2. Select .truck file for operations")
        print("--- Other related operations ---")
        print("101. Create new torquecurve")
        print("-1. Exit program")
        try:
            option = int(input("Enter choice: "))
        except:
            option = 0
        match(option):
            case (1):
                try:
                    fname = input("Enter .truck file name to open: ")
                    check = open(fname, mode='r')
                    check.close()
                except:
                    print("File not found or error in reading file")
                    continue
                check2 = fname.find(".truck")
                if check2==-1:
                    choice = input("Not a .truck file\nEnter yes to continue or anything else to return to menu: ")
                    if choice=="yes":
                        check2 = 0
    
                if check2>-1:
                    t = Truck(fname,n)
                    truckfiles.append(t)
                    check = t.read_truck()
                    if check:
                        
                        print("Added ",t.file," at position ",n)
                        n+=1
                    else:
                        t = truckfiles.pop()
                        print("Didn't recognize .truck file!")
                        del t
                else:
                    print("Returning to menu")
            case (2) if n>0:
                print(".truck files currently open:")
                i_pos = 0
                for i in truckfiles:
                    print(i_pos," ",i.file)
                    i_pos+=1
                try:
                    pos = int(input("Enter position of .truck file to open: "))
                except:
                    pos = -1
                if pos<0 or pos>=n:
                    print("Out of bounds")
                else:
                    truckfiles[pos].menu()
                
            case (101):
                new_torquecurve()
            case (-1):
                print("Exiting")
            case _:
                print("Option unavailable")
    return

#main code
print("truck-operations.py - Version 0.1.1")
print("Author: Ra1pid")
option = input("Press enter to continue, or enter info for more information\n")
if option.find("info")>-1:
    print("Made as a tool for various operations on .truck files for RoR.\nI originally developed this for my Small Forest Rally project, to convert the trees in Blender to coordinates for the map.\n\nNavigation through the menus is like this:\nX. *desired option*\nEnter choice: X\nDocumentation for each function can be found in program-functionality.txt.\nHope this tool works for you\n- Ra1pid\n")
menu()
