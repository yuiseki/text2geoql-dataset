[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["shop"~"clothes"](area.outer);
);
out geom;
