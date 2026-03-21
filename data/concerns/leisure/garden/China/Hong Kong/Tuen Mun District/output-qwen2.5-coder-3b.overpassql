[out:json][timeout:30];
area["name:en"="Tuen Mun District"]->.outer;
(
  nwr["leisure"~"garden"](area.outer);
);
out geom;
