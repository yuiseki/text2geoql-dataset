[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["historic"~"monument"](area.outer);
);
out geom;
