[out:json][timeout:30];
area["name:ja"="東京都"]->.outer;
(
  nwr["tourism"="zoo"](area.outer);
);
out geom;
