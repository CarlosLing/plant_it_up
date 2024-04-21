import {
  Container,
  Flex,
  Heading,
  Skeleton,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { SensorService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"

export const Route = createFileRoute("/_layout/sensors")({
  component: Sensors,
})

function SensorsTableBody() {
  const { data: sensors } = useSuspenseQuery({
    queryKey: ["sensors"],
    queryFn: () => SensorService.listSensors({}),
  })

  return (
    <Tbody>
      {sensors.data.map((sensor) => (
        <Tr key={sensor.id}>
          <Td>{sensor.id}</Td>
          <Td>{sensor.name}</Td>
          <Td>{sensor.measurement}</Td>
          <Td>{sensor.location}</Td>
          <Td color={!sensor.description ? "ui.dim" : "inherit"}>
            {sensor.description || "N/A"}
          </Td>
          <Td>
            <ActionsMenu type={"Sensor"} value={sensor} />
          </Td>
        </Tr>
      ))}
    </Tbody>
  )
}

function SensorsTable() {
  return (
    <TableContainer>
      <Table size={{ base: "sm", md: "md" }}>
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Name</Th>
            <Th>Measurement</Th>
            <Th>Location</Th>
            <Th>Description</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <ErrorBoundary
          fallbackRender={({ error }) => (
            <Tbody>
              <Tr>
                <Td colSpan={6}>Something went wrong: {error.message}</Td>
              </Tr>
            </Tbody>
          )}
        >
          <Suspense
            fallback={
              <Tbody>
                {new Array(5).fill(null).map((_, index) => (
                  <Tr key={index}>
                    {new Array(6).fill(null).map((_, index) => (
                      <Td key={index}>
                        <Flex>
                          <Skeleton height="20px" width="20px" />
                        </Flex>
                      </Td>
                    ))}
                  </Tr>
                ))}
              </Tbody>
            }
          >
            <SensorsTableBody />
          </Suspense>
        </ErrorBoundary>
      </Table>
    </TableContainer>
  )
}

function Sensors() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Sensor Management
      </Heading>

      <Navbar type={"Sensor"} />
      <SensorsTable />
    </Container>
  )
}
