[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["leisure"~"park"](area.outer);
);
out geom;
