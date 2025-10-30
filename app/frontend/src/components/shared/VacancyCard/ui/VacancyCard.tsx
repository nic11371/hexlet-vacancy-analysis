import React from "react";
import type { VacancyCardProps } from "../../../../types";
import { Card, Group, Text, Badge, Button, Stack, Box } from '@mantine/core';
import { Building2, MapPin } from "lucide-react";
import { Link } from "@inertiajs/react";

export const VacancyCard: React.FC<VacancyCardProps> = ({ id, title, url, salary, employment, company, city, skills }) => {
  return (
    <Link href={url || `/vacancies/${id}`} style={{ textDecoration: 'none' }}>
     <Card shadow="sm" padding="lg" radius="md" withBorder mx="auto" style={{ width: '100%'}}>
      {/* Десктопная версия */}
      <Group justify="space-between" wrap="nowrap" visibleFrom="sm">
        {/* Левая часть */}
        <Box style={{ flex: 1 }} maw='60%'>
          <Stack gap='xs'>
            {/* Название вакансии */}
            <Text fw={700} size="xl" c="#0d2e4e">{title}</Text>

            {/* Информация о компании */}
            <Group gap='xs'>
              {company && (
                <Group gap={5}>
                  <Building2 size={16} />
                  <Text size="md">{company.name}</Text>
                </Group>
              )}
              {city && (
                <Group gap={5}>
                  <MapPin size={16} />
                  <Text>{city.name}</Text>
                </Group>
              )}
              <Badge color="#20B0B4">{employment}</Badge>
            </Group>

            {/* Навыки */}
            <Group wrap="wrap" gap="xs">
              {skills.map((skill) => (
                <Badge 
                  key={skill} 
                  color="#20B0B4"
                  variant="outline"
                  style={{ width: 'auto' }}
                >
                  {skill}
                </Badge>
              ))}
            </Group>
          </Stack>
        </Box>

        {/* Правая часть */}
        <Stack gap="md" align="flex-end">
          <Text size="xl" fw={700} c='#20B0B4'>{salary}</Text>
          <Button 
            w='fit-content' 
            color="#20B0B4" 
            radius='md'
            onClick={(e) => e.preventDefault()}
          >
            Откликнуться
          </Button>
        </Stack>
      </Group>

      {/* Мобильная версия */}
      <Stack gap="md" hiddenFrom="sm">
        {/* Название вакансии */}
        <Text fw={700} size="xl" c="#0d2e4e">{title}</Text>

        {/* Компания и город */}
        <Group gap='xs'>
          {company && (
            <Group gap={5}>
              <Building2 size={16} />
              <Text size="md">{company.name}</Text>
            </Group>
          )}
          {city && (
            <Group gap={5}>
              <MapPin size={16} />
              <Text>{city.name}</Text>
            </Group>
          )}
        </Group>

        {/* Формат работы */}
        <Badge color="#20B0B4" w="fit-content">{employment}</Badge>

        {/* Зарплата */}
        <Text size="xl" fw={700} c='#20B0B4'>{salary}</Text>

        {/* Навыки */}
        <Group wrap="wrap" gap="xs">
          {skills.map((skill) => (
            <Badge 
              key={skill} 
              color="#20B0B4"
              variant="outline"
              size="md"
              style={{ width: 'auto' }}
            >
              {skill}
            </Badge>
          ))}
        </Group>

        <Button color="#20B0B4" radius='md' fullWidth>Откликнуться</Button>
      </Stack>
    </Card>
    </Link>
  );
};