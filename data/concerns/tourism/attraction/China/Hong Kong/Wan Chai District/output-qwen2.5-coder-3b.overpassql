[out:json][timeout:30];
area["name:en"="Wan Chai District"][boundary=administrative]->.outer;
(
  nwr["tourism"="attraction"](area.outer);
);
out geom;
