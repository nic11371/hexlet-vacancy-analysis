import { VacancyCard } from "../shared/VacancyCard";
import { usePage } from "@inertiajs/react";
import type { VacancyCardProps } from "../../types";
import type React from "react";
import { Card } from "@mantine/core";

interface HomePageProps {
  vacancies: VacancyCardProps[];
  [key: string]: any;
}

const HomePage: React.FC = () => {
  const { props } = usePage<HomePageProps>()
  console.log(props.vacancies);
  return (
    <div>
      <h1 className="text-3xl font-bold">Главная</h1>
      <p className="mt-4">Информация.</p>
      <Card>
        {props.vacancies.map((vacancy) => (
          <Card key={vacancy.id}>
              <VacancyCard 
              id={vacancy.id}
              title={vacancy.title}
              salary={vacancy.salary}
              company={vacancy.company}
              city={vacancy.city}
              employment={vacancy.employment}
              skills={vacancy.skills}
              url={vacancy.url}
            />
          </Card>
        ))}
      </Card>
    </div>
  );
};

export default HomePage;