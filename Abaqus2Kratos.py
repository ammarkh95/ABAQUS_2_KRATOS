import csv
from itertools import islice, dropwhile, takewhile
from copy import deepcopy

#################   Nodes Read Started #######################

# Read File Name Number of Nodes and Elements

No_Nodes = int(157589)
No_Elements = int(867833)

with open ("ABAQUSCYLINDER.inp", newline='') as box:
    reader = csv.reader(box,delimiter=',')
    all(next(reader) for i in range(9))

    NodeData =[]
    for row in islice(reader,0,No_Nodes):
        node_id =int(row[0])
        x_c= float(row[1])
        y_c= float(row[2])
        z_c= float(row[3])

        NodeData.append([node_id,x_c,y_c,z_c])

#################   Nodes Read Completed #######################

#################   Elements Read Started #######################

    header = next(reader) # skip header after Node Read

    ElementData =[]  # Tetrahedral elements with 4 nodes
    for row in islice(reader,0,No_Elements):
        element_id =int(row[0])
        n1= int(row[1])
        n2= int(row[2])
        n3= int(row[3])
        n4= int(row[4])

        ElementData.append([element_id,int(0),n1,n2,n3,n4])

#################   Elements Read Completed #######################

#################   Conditions Read Started #######################

    # Declare Storage arrays

    InletNodes = []
    InletElements = []
    NoSlipElements = []
    NoSlipNodes = []
    OutletElements = []
    OutletNodes = []

    all(next(reader) for i in range(11)) # skip headers after Elements Read

    Inlet_Nodes = takewhile(lambda _line: " elset=Inlet"  not in _line, reader) # Inlet Nodes

    Inlet_Elements = takewhile(lambda _line: " nset=NoSlip"  not in _line, reader) #Inlet Elements

    NoSlip_Nodes = takewhile(lambda _line: " elset=NoSlip"  not in _line, reader) # NoSlip Nodes
 
    NoSlip_Elements = takewhile(lambda _line: " nset=Outlet"  not in _line, reader)  #NoSlip Elements

    Outlet_Nodes = takewhile(lambda _line: " elset=Outlet"  not in _line, reader) # OutletNodes

    Outlet_Elements = takewhile(lambda _line: "*End Assembly"  not in _line, reader) #OutletElements

    for line in Inlet_Nodes:
        InletNodes.append(line)

    for line in Inlet_Elements:
        InletElements.append(line)

    for line in NoSlip_Nodes:
        NoSlipNodes.append(line)   

    for line in NoSlip_Elements:
        NoSlipElements.append(line)

    for line in Outlet_Nodes:
        OutletNodes.append(line)

    for line in Outlet_Elements:
        OutletElements.append(line)

    #  Extract Nodes defining normal for every cell (last three nodes)

    Surf_Conditions=[[each_list[i] for i in (3,4,5)] for each_list in ElementData]

    #  Flattening Lists for ease of processing and writing

    InletElements= [item1 for sublist1 in InletElements for item1 in sublist1]
    NoSlipElements= [item2 for sublist2 in NoSlipElements for item2 in sublist2]
    OutletElements=[item3 for sublist3 in OutletElements for item3 in sublist3]

    InletNodes= [item4 for sublist4 in InletNodes for item4 in sublist4]
    NoSlipNodes= [item5 for sublist5 in NoSlipNodes for item5 in sublist5]
    OutletNodes=[item6 for sublist6 in OutletNodes for item6 in sublist6]

    #  Declare Surface Conditions lists for BC'S

    Inlet_Surf_Conditions=[]

    NoSlip_Surf_Conditions=[]

    Outlet_Surf_Conditions=[]

#######################################################

    # Filling Inlet Conditions

    for i in InletElements:           
        Inlet_Surf_Conditions.append(Surf_Conditions[int(i)-1])
    
  
#######################################################

    # Filling No Slip Conditions

    for i in NoSlipElements:           
        NoSlip_Surf_Conditions.append(Surf_Conditions[int(i)-1])


#######################################################

    # Filling Outlet Conditions

    for i in OutletElements:           
        Outlet_Surf_Conditions.append(Surf_Conditions[int(i)-1])

#######################################################

    # Building All Surface Conditions for the model and filtering repeated ones

    Boundary_Surf_cond = Inlet_Surf_Conditions+ NoSlip_Surf_Conditions+Outlet_Surf_Conditions

    seen_Filter = set()
    Boundary_Surf_cond_Filter = []
    for x in Boundary_Surf_cond:
        if frozenset(x) not in seen_Filter:
            Boundary_Surf_cond_Filter.append(x)
            seen_Filter.add(frozenset(x))

    Inlet_Surf_Conditions_Filter=[deepcopy(l1) for l1 in Inlet_Surf_Conditions if l1 in Boundary_Surf_cond_Filter] 
    NoSlip_Surf_Conditions_Filter=[deepcopy(l2) for l2 in NoSlip_Surf_Conditions if l2 in Boundary_Surf_cond_Filter and (l2 not in Inlet_Surf_Conditions and l2 not in Outlet_Surf_Conditions)] 
    Outlet_Surf_Conditions_Filter=[deepcopy(l3) for l3 in Outlet_Surf_Conditions if l3 in Boundary_Surf_cond_Filter] 
      

    for e in range(len(Inlet_Surf_Conditions_Filter)):
        Inlet_Surf_Conditions_Filter[e].insert(0,e+1)
        Inlet_Surf_Conditions_Filter[e].insert(1,0)


    for e in range(len(NoSlip_Surf_Conditions_Filter)):
        NoSlip_Surf_Conditions_Filter[e].insert(0,len(Inlet_Surf_Conditions_Filter)+e+1)
        NoSlip_Surf_Conditions_Filter[e].insert(1,0)


    for e in range(len(Outlet_Surf_Conditions_Filter)):
        Outlet_Surf_Conditions_Filter[e].insert(0,len(Inlet_Surf_Conditions_Filter)+len(NoSlip_Surf_Conditions_Filter)+e+1)
        Outlet_Surf_Conditions_Filter[e].insert(1,0)

    Boundary_Surf_cond_Filter = Inlet_Surf_Conditions_Filter+NoSlip_Surf_Conditions_Filter+Outlet_Surf_Conditions_Filter

    # print(len(Boundary_Surf_cond_Filter))

#################   Conditions Read Completed #######################



#################  Mdpa file write Started #######################

with open('Cylinder.mdpa', 'w', newline='') as boxmesh:
    boxmesh.write('Begin ModelPartData\n')
    boxmesh.write('//  VARIABLE_NAME value\n')
    boxmesh.write('End ModelPartData\n\n')
    boxmesh.write('Begin Properties 0\n')
    boxmesh.write('End Properties\n\n')
    boxmesh.write('Begin Nodes\n')
    writer= csv.writer(boxmesh,delimiter='\t')
    for entries in NodeData:
        writer.writerow(entries)
    boxmesh.write('End Nodes\n')
    boxmesh.write('\nBegin Elements Element3D4N// GUI group identifier: Parts Auto1\n')
    for entries in ElementData:
        writer.writerow(entries)
    boxmesh.write('End Elements\n')
    boxmesh.write('\nBegin Conditions SurfaceCondition3D3N// GUI group identifier: _HIDDEN__SKIN_\n')
    for entries in Boundary_Surf_cond_Filter:
          writer.writerow(entries)
    boxmesh.write('End Conditions\n')
    boxmesh.write('\n\nBegin SubModelPart Parts_Parts_Auto1 // Group Parts Auto1 // Subtree Parts\n')
    boxmesh.write('\tBegin SubModelPartNodes\n')
    for item in [row[0] for row in NodeData]:
        boxmesh.write("%s\n" % item)
    boxmesh.write('\tEnd SubModelPartNodes\n')
    boxmesh.write('\tBegin SubModelPartElements\n')
    for item in [row[0] for row in ElementData]:
        boxmesh.write("%s\n" % item)
    boxmesh.write('\tEnd SubModelPartElements\n')
    boxmesh.write('\tBegin SubModelPartConditions\n')
    boxmesh.write('\tEnd SubModelPartConditions\n')
    boxmesh.write('End SubModelPart\n\n')
    boxmesh.write('Begin SubModelPart AutomaticInlet3D_Automatic_inlet_velocity_Auto1 // Group Automatic inlet velocity Auto1 // Subtree AutomaticInlet3D\n')
    boxmesh.write('\tBegin SubModelPartNodes\n')
    for item  in InletNodes:
        boxmesh.write("%s\n" % int(item))
    boxmesh.write('\tEnd SubModelPartNodes\n')
    boxmesh.write('\tBegin SubModelPartElements\n')
    boxmesh.write('\tEnd SubModelPartElements\n')
    boxmesh.write('\tBegin SubModelPartConditions\n')
    for item in [row[0] for row in Inlet_Surf_Conditions_Filter]:
        boxmesh.write("%s\n" % int(item))
    boxmesh.write('\tEnd SubModelPartConditions\n')
    boxmesh.write('End SubModelPart\n\n')

    boxmesh.write('Begin SubModelPart Outlet3D_Outlet_pressure_Auto1 // Group Outlet pressure Auto1 // Subtree Outlet3D\n')
    boxmesh.write('\tBegin SubModelPartNodes\n')
    for item  in OutletNodes:
        boxmesh.write("%s\n" % int(item))
    boxmesh.write('\tEnd SubModelPartNodes\n')
    boxmesh.write('\tBegin SubModelPartElements\n')
    boxmesh.write('\tEnd SubModelPartElements\n')
    boxmesh.write('\tBegin SubModelPartConditions\n')
    for item in [row[0] for row in Outlet_Surf_Conditions_Filter]:
        boxmesh.write("%s\n" % int(item))
    boxmesh.write('\tEnd SubModelPartConditions\n')
    boxmesh.write('End SubModelPart\n\n')

    boxmesh.write('Begin SubModelPart NoSlip3D_No_Slip_Auto1 // Group No Slip Auto1 // Subtree NoSlip3D\n')
    boxmesh.write('\tBegin SubModelPartNodes\n')
    for item  in NoSlipNodes:
        boxmesh.write("%s\n" % int(item))
    boxmesh.write('\tEnd SubModelPartNodes\n')
    boxmesh.write('\tBegin SubModelPartElements\n')
    boxmesh.write('\tEnd SubModelPartElements\n')
    boxmesh.write('\tBegin SubModelPartConditions\n')
    for item in [row[0] for row in NoSlip_Surf_Conditions_Filter]:
        boxmesh.write("%s\n" % int(item))
    boxmesh.write('\tEnd SubModelPartConditions\n')
    boxmesh.write('End SubModelPart\n\n')
