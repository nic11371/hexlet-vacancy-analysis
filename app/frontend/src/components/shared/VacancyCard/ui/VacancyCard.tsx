import type React from "react";
import type { VacancyCardProps } from "../model/types";

export const VacancyCard:React.FC<VacancyCardProps> = ({ id, title, url, salary, employment, company, city, skills }) => {
  return (
    <div>
      <h3>{title}</h3>
      <p>{id}</p>
      <p>{url}</p>
      <p>{salary}</p>
      <p>{employment}</p>
      <p>{company ? company.name : 'Без компании'}</p>
      <p>{city ? city.name : 'Без города'}</p>
      <p>{skills.join(',')}</p>
    </div>
  )
}