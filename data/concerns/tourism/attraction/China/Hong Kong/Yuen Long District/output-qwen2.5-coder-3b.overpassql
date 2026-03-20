[out:json][timeout:30];
area["name:en"="Yuen Long District"][boundary=administrative]->.outer;
(
  nwr["tourism"="attraction"](area.outer);
);
out geom;
