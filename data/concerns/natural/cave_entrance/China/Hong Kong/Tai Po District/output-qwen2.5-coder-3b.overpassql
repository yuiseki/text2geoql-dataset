[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh"="香港"];
(
  nwr["natural"="cave"](area.outer);
);
out geom;
