[out:json][timeout:30];
area["name:en"="Tuen Mun District"]->.outer;
(
  nwr["leisure"~"horse_riding"](area.outer);
);
out geom;
