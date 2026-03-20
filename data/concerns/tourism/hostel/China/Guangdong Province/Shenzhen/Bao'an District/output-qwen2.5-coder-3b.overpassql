[out:json][timeout:30];
area["name:en"="Guangdong Province"][boundary=administrative]->.outer;
(
  nwr["tourism"="hostel"](area.outer);
);
out geom;
