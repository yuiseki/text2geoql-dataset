[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh"="香港"];
(
  nwr["leisure"="fishing"](area.outer);
);
out geom;
