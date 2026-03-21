[out:json][timeout:30];
area["name:en"="Sai Kung District"]->.outer;
(
  nwr["leisure"~"horse_riding"](area.outer);
);
out geom;
