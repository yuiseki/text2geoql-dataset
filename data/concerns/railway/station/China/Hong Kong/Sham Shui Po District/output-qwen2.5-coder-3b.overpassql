[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
