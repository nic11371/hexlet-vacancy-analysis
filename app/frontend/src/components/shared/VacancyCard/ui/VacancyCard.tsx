import type React from "react";
import type { VacancyCardProps } from "../model/types";
import { Card, Badge, Text, Group, Stack, Button } from '@mantine/core';
import { Building2, MapPin } from "lucide-react";

export const VacancyCard:React.FC<VacancyCardProps> = ({ id, title, url, salary, employment, company, city, skills }) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder mx="auto" style={{ width: '100%'}}>
      <Group justify="space-between">
        <Text fw={700} size="xl" c="#0d2e4e">{title}</Text>
        <Text size="xl" fw={700} c='#20B0B4'>{salary}</Text>
      </Group>
      <Group justify="space-between">
        <Group>
          <Stack>
            <Group>
              <Group gap={5}>
                <Building2 />
                <Text size="md">{company ? company.name : ''}</Text>
              </Group>
              {city && (
                <Group gap={5}>
                  <MapPin />
                  <Text>{city ? city.name : ''}</Text>
                </Group>
              )}
            <Badge color="#20B0B4">{employment}</Badge>
            </Group>
            <Group>
              {skills.map((skill) => (
                <Group key={skill}>
                  <Badge color="#20B0B4">{skill}</Badge>
                </Group>
              ))}
            </Group>
          </Stack>
        </Group>
        <Button color="#20B0B4">Откликнуться</Button>
      </Group>
    </Card>
  )
}