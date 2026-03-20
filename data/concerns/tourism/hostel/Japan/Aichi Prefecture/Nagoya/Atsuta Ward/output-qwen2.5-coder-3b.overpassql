[out:json][timeout:30];
area["name:en"="Aichi Prefecture"][boundary=administrative]->.outer;
(
  nwr["tourism"="hostel"](area.outer);
);
out geom;
