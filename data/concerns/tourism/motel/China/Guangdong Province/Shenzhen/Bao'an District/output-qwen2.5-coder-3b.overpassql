[out:json][timeout:30];
area["name:en"="Guangdong Province"][boundary=administrative]->.outer;
(
  nwr["tourism"="motel"](area.outer);
);
out geom;
