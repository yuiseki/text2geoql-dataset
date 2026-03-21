[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
