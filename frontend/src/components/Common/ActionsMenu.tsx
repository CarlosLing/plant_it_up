import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { ItemPublic, UserPublic, SensorPublic } from "../../client"
import EditUser from "../Admin/EditUser"
import EditItem from "../Items/EditItem"
import EditSensor from "../Sensors/EditSensor"
import Delete from "./DeleteAlert"

interface ActionsMenuProps {
  type: string
  value: ItemPublic | UserPublic | SensorPublic
  disabled?: boolean
}

function renderEditComponent(type: string, value: any, isOpen: boolean, onClose: () => void) {
  switch (type) {
    case "User":
      return (
        <EditUser
          user={value as UserPublic}
          isOpen={isOpen}
          onClose={onClose}
        />
      );
    case "Item":
      return (
        <EditItem
          item={value as ItemPublic}
          isOpen={isOpen}
          onClose={onClose}
        />
      );
    case "Sensor":
      return (
        <EditSensor
          sensor={value as SensorPublic}
          isOpen={isOpen}
          onClose={onClose}
        />
      );
    default:
      return null; // Or handle unexpected types appropriately
  }
}


const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const deleteModal = useDisclosure()

  return (
    <>
      <Menu>
        <MenuButton
          isDisabled={disabled}
          as={Button}
          rightIcon={<BsThreeDotsVertical />}
          variant="unstyled"
        />
        <MenuList>
          <MenuItem
            onClick={editUserModal.onOpen}
            icon={<FiEdit fontSize="16px" />}
          >
            Edit {type}
          </MenuItem>
          <MenuItem
            onClick={deleteModal.onOpen}
            icon={<FiTrash fontSize="16px" />}
            color="ui.danger"
          >
            Delete {type}
          </MenuItem>
        </MenuList>
        {renderEditComponent(type, value, editUserModal.isOpen, editUserModal.onClose)}
        <Delete
          type={type}
          id={value.id}
          isOpen={deleteModal.isOpen}
          onClose={deleteModal.onClose}
        />
      </Menu>
    </>
  )
}

export default ActionsMenu
