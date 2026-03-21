[out:json][timeout:30];
area["name:en"="Tuen Mun District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
