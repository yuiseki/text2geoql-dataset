[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["shop"~"second_hand"](area.outer);
);
out geom;
