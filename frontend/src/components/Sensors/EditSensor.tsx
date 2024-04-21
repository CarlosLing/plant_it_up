import {
    Button,
    FormControl,
    FormErrorMessage,
    FormLabel,
    Input,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
    type ApiError,
    type SensorPublic,
    type SensorUpdate,
    SensorService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface EditSensorProps {
    sensor: SensorPublic
    isOpen: boolean
    onClose: () => void
}

const EditSensor = ({ sensor, isOpen, onClose }: EditSensorProps) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToast()
    const {
        register,
        handleSubmit,
        reset,
        formState: { isSubmitting, errors, isDirty },
    } = useForm<SensorUpdate>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: sensor,
    })

    const mutation = useMutation({
        mutationFn: (data: SensorUpdate) =>
            SensorService.updateSensor({ id: sensor.id, requestBody: data }),
        onSuccess: () => {
            showToast("Success!", "Sensor updated successfully.", "success")
            onClose()
        },
        onError: (err: ApiError) => {
            const errDetail = (err.body as any)?.detail
            showToast("Something went wrong.", `${errDetail}`, "error")
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["sensors"] })
        },
    })

    const onSubmit: SubmitHandler<SensorUpdate> = async (data) => {
        mutation.mutate(data)
    }

    const onCancel = () => {
        reset()
        onClose()
    }

    return (
        <>
            <Modal
                isOpen={isOpen}
                onClose={onClose}
                size={{ base: "sm", md: "md" }}
                isCentered
            >
                <ModalOverlay />
                <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
                    <ModalHeader>Edit Sensor</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <FormControl isInvalid={!!errors.name}>
                            <FormLabel htmlFor="title">Name</FormLabel>
                            <Input
                                id="title"
                                {...register("name", {
                                    required: "Name is required",
                                })}
                                type="text"
                            />
                            {errors.name && (
                                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
                            )}
                        </FormControl>
                        <FormControl isInvalid={!!errors.measurement}>
                            <FormLabel htmlFor="title">Measurement</FormLabel>
                            <Input
                                id="title"
                                {...register("measurement", {
                                    required: "Measurement is required",
                                })}
                                type="text"
                            />
                            {errors.measurement && (
                                <FormErrorMessage>{errors.measurement.message}</FormErrorMessage>
                            )}
                        </FormControl>
                        <FormControl isInvalid={!!errors.location}>
                            <FormLabel htmlFor="title">Location</FormLabel>
                            <Input
                                id="title"
                                {...register("location", {
                                    required: "Location is required",
                                })}
                                type="text"
                            />
                            {errors.location && (
                                <FormErrorMessage>{errors.location.message}</FormErrorMessage>
                            )}
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel htmlFor="description">Description</FormLabel>
                            <Input
                                id="description"
                                {...register("description")}
                                placeholder="Description"
                                type="text"
                            />
                        </FormControl>
                    </ModalBody>
                    <ModalFooter gap={3}>
                        <Button
                            variant="primary"
                            type="submit"
                            isLoading={isSubmitting}
                            isDisabled={!isDirty}
                        >
                            Save
                        </Button>
                        <Button onClick={onCancel}>Cancel</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default EditSensor
