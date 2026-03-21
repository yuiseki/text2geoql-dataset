[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["historic"~"monument"](area.outer);
);
out geom;
