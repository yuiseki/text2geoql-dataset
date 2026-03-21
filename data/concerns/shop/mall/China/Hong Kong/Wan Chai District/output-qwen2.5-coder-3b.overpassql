[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
