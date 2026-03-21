[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["leisure"~"horse_riding"](area.outer);
);
out geom;
