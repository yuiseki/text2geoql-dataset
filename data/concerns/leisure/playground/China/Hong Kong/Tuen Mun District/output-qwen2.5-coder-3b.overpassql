[out:json][timeout:30];
area["name:en"="Tuen Mun District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
