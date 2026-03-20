[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
